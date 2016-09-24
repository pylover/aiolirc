import asyncio

from libc.stdlib cimport calloc, free
from posix cimport fcntl, unistd
from cpython.exc cimport PyErr_WarnEx

from aiolirc.compat import aiter_compat
from aiolirc.exceptions import LIRCInitError, LIRCAbuseError, LIRCDeinitError, TranslateDone, LIRCNextCodeError, \
    LIRCLoadConfigError, TranslateError, LIRCConfigInitError
from aiolirc.c_lirc_client cimport lirc_freeconfig, lirc_readconfig, lirc_code2char, lirc_init, lirc_deinit, \
    lirc_nextcode, lirc_config

cdef char * ENCODING = "utf-8"
cdef int STRING_BUFFER_LEN = 256


cdef class LIRCConfig:
    cdef:
        lirc_config * _c_lirc_config

    def __cinit__(self, config_filename):
        self.add_config_file(config_filename)

    def __dealloc__(self):
        if self._c_lirc_config is not NULL:
            lirc_freeconfig(self._c_lirc_config)

    cdef void add_config_file(LIRCConfig self, unicode config_filename):
        b_config_filename = config_filename.encode(ENCODING)

        if b_config_filename is not None:
            lirc_readconfig(
                b_config_filename, &self._c_lirc_config, NULL)
        else:
            lirc_readconfig(
                NULL, &self._c_lirc_config, NULL)

        if self._c_lirc_config is NULL:
            raise LIRCLoadConfigError('Could not load the config file (%s)' % config_filename)

    cdef public unicode translate(LIRCConfig self, char * code):
        """
        Translate the (byte) string associated with the code in the lircrc config file
        """
        self._ensure_init()

        cdef char * string_buf = \
            <char * >calloc(STRING_BUFFER_LEN, sizeof(char))
        cdef char * string_buf_2 = string_buf  # string_buf might be destroyed

        status = lirc_code2char(self._c_lirc_config, code, &string_buf)

        if status == -1:
            free(string_buf)
            raise TranslateError("There was an error determining the config string.")

        if string_buf == NULL:
            free(string_buf_2)
            raise TranslateDone()
        else:
            string = string_buf.decode(ENCODING)
            free(string_buf_2)
            return string

    cdef void _ensure_init(LIRCConfig self):
        if self._c_lirc_config is NULL:
            raise LIRCConfigInitError('%s has not been initialised.' % self.__name__)


cdef object initialized = <bint>0
cdef LIRCConfig lircrc_config = None

_locks = {}


cdef class LIRCClient:
    cdef:
        public unicode lircrc_file, lircrc_prog
        public float _check_interval
        public bint verbose, _blocking
        public object _loop
        int _lirc_socket

    def __cinit__(self, lircrc_prog, *, lircrc_file='~/.config/lircrc',
                 loop=None, check_interval=.05, verbose=False, blocking=False):
        self.lircrc_file = lircrc_file
        self.lircrc_prog = lircrc_prog
        self._check_interval = check_interval
        self._loop = loop or asyncio.get_event_loop()
        self._lirc_socket = -2
        self._blocking = blocking

    cpdef void load_config_file(LIRCClient self, unicode lircrc_file):
        global lircrc_config
        self._ensure_init()

        if lircrc_config is not None:
            lircrc_config.add_config_file(lircrc_file)
        else:
            lircrc_config = LIRCConfig(lircrc_file)

    cpdef void lirc_init(LIRCClient self):
        global initialized
        if initialized:
            PyErr_WarnEx(UserWarning, "lirc is already initialized.", 1)
            return

        # init lirc
        b_program_name = self.lircrc_prog.encode(ENCODING)
        self._lirc_socket = lirc_init(b_program_name, self.verbose)
        if self._lirc_socket == -1:
            raise LIRCInitError("Unable to initialize lirc (socket was -1 from C library).")

        # Configure blocking
        fcntl.fcntl(self._lirc_socket, fcntl.F_SETOWN, unistd.getpid())
        flags = fcntl.fcntl(self._lirc_socket, fcntl.F_GETFL, 0)
        flags = (flags & ~fcntl.O_NONBLOCK) | (0 if self._blocking else fcntl.O_NONBLOCK)
        fcntl.fcntl(self._lirc_socket, fcntl.F_SETFL, flags)


        # Setting the initialization lock flag
        initialized = True

        # Loading the lircrc file
        if self.lircrc_file is not None:
            self.load_config_file(self.lircrc_file)

    cpdef void lirc_deinit(LIRCClient self):
        global initialized, lircrc_config
        if not initialized:
            PyErr_WarnEx(UserWarning, "lirc is not initialized yet.", 1)
            return

        if lirc_deinit() == -1:
            raise LIRCDeinitError("Unable to de-initialize lirc.")

        lircrc_config = None
        initialized = False

    cpdef void lirc_ignore_nextcode(LIRCClient self):
        cdef char * code = NULL
        try:
            if lirc_nextcode(&code) == -1:  # Error !
                raise LIRCNextCodeError("There was an error reading the next code.")
        finally:
            free(code)

    cpdef unicode lirc_nextcode(LIRCClient self):
        global lircrc_config
        cdef char * code = NULL
        try:
            if lirc_nextcode(&code) == -1:  # Error !
                raise LIRCNextCodeError("There was an error reading the next code.")

            if code == NULL:
                return None
            else:
                return lircrc_config.translate(code)
        except TranslateDone:
            return None
        finally:
            free(code)

    def _ensure_async(LIRCClient self not None):
        if self._blocking:
            raise LIRCAbuseError(
                'Cannot use `Asynchronous Iterator` and `Asynchronous Context Manager` when blocking is True.')

    def _ensure_init(LIRCClient self not None):
        if not initialized:
            raise LIRCInitError('%s has not been initialized.' % self.__name__)

    # Asynchronous Context Manager
    async def __aenter__(LIRCClient self not None):
        await self.lock
        self._ensure_async()
        self.lirc_init()
        return self

    async def __aexit__(LIRCClient self not None, exc_type, exc_val, exc_tb):
        self.lirc_deinit()
        self.lock.release()

    # Asynchronous Iterator
    def __aiter__(LIRCClient self not None):
        self._ensure_async()
        return aiter_compat(self)

    async def __anext__(LIRCClient self not None):
        while True:
            command = self.lirc_nextcode()
            if command is None:
                await asyncio.sleep(self.check_interval)
                continue
            else:
                return command

    @property
    def lock(LIRCClient self not None):
        global _locks
        if self.lircrc_prog not in _locks:
            _locks[self.lircrc_prog] = asyncio.Lock()
        return _locks[self.lircrc_prog]

    @property
    def blocking(LIRCClient self not None):
        return self._blocking

    @property
    def check_interval(self):
        return self._check_interval

    def ignore(LIRCClient self not None):
        return IgnoreContext(self)


cdef class IgnoreContext:
    cdef:
        LIRCClient _source
        object _future

    def __cinit__(IgnoreContext self, LIRCClient source):
        self._source = source

    async def capture_and_ignore(IgnoreContext self not None):
        while True:
            self._source.lirc_ignore_nextcode()
            await asyncio.sleep(self._source.check_interval)

    # Asynchronous Context Manager
    async def __aenter__(IgnoreContext self not None):
        self._future = asyncio.ensure_future(self.capture_and_ignore())
        return self

    async def __aexit__(IgnoreContext self not None, exc_type, exc_val, exc_tb):
        self._future.cancel()
        await asyncio.wait([self._future])


