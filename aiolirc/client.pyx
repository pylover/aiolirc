import asyncio

from libc.stdlib cimport free
from posix cimport fcntl, unistd
from cpython.exc cimport PyErr_WarnEx

from aiolirc cimport c_lirc_client
from aiolirc.compat import aiter_compat
from aiolirc.constants import ENCODING
from aiolirc.exceptions import LIRCInitError, LIRCAbuseError, LIRCDeinitError, TranslateDone, LIRCNextCodeError
from aiolirc cimport config


cdef object initialized = <bint>0
cdef config.LIRCConfig lircrc_config = None

cdef dict _locks = {}  # TODO: lock


cdef class LIRCClient(object):

    def __init__(self, lircrc_prog, *, lircrc_file='~/.config/lircrc', loop=None, check_interval=.05, max_stack_size=10,
                 empty_skip=5, verbose=False, blocking=False):
        self.lircrc_file = lircrc_file
        self.lircrc_prog = lircrc_prog
        self.check_interval = check_interval
        self._loop = loop or asyncio.get_event_loop()
        self._lirc_socket = -2
        self._blocking = blocking

    @property
    def blocking(LIRCClient self not None):
        return self._blocking

    @blocking.setter
    def blocking(LIRCClient self not None, bint v):
        if v is not self._blocking:
            self._blocking = v
            self.update_blocking()

    cdef void load_config_file(LIRCClient self, unicode lircrc_file):
        global lircrc_config
        self._ensure_init()

        b_lircrc_filename = lircrc_file.encode(ENCODING)

        if lircrc_config is not None:
            lircrc_config.add_config_file(b_lircrc_filename)
        else:
            lircrc_config = config.LIRCConfig(b_lircrc_filename)

    cdef void update_blocking(LIRCClient self):
        fcntl.fcntl(self._lirc_socket, fcntl.F_SETOWN, unistd.getpid())
        flags = fcntl.fcntl(self._lirc_socket, fcntl.F_GETFL, 0)
        flags = (flags & ~fcntl.O_NONBLOCK) | (0 if self._blocking else fcntl.O_NONBLOCK)
        fcntl.fcntl(self._lirc_socket, fcntl.F_SETFL, flags)

    cdef void lirc_init(LIRCClient self):
        global initialized
        if initialized:
            PyErr_WarnEx(UserWarning, "lirc is already initialized.", 1)
            return

        # init lirc
        b_program_name = self.lircrc_prog.encode(ENCODING)
        self._lirc_socket = c_lirc_client.lirc_init(b_program_name, self.verbose)
        if self._lirc_socket == -1:
            raise LIRCInitError("Unable to initialize lirc (socket was -1 from C library).")

        # Configure blocking
        self.update_blocking()

        # Setting the initialization lock flag
        initialized = True

        # Loading the lircrc file
        if self.lircrc_file is not None:
            self.load_config_file(self.lircrc_file)

    cdef void lirc_deinit(LIRCClient self):
        global initialized, lircrc_config
        if not initialized:
            PyErr_WarnEx(UserWarning, "lirc is not initialized yet.", 1)
            return

        if c_lirc_client.lirc_deinit() == -1:
            raise LIRCDeinitError("Unable to de-initialize lirc.")

        lircrc_config = None
        initialized = False

    cdef unicode lirc_nextcode(LIRCClient self):
        global lircrc_config
        cdef char * code = NULL
        try:
            if c_lirc_client.lirc_nextcode(&code) == -1:  # Error !
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

    # Lock
    @property
    def _lock(LIRCClient self not None):
        key = (self.lircrc_prog, self)
        return 

    # Asynchronous Context Manager
    async def __aenter__(LIRCClient self not None):
        self._ensure_async()
        self.lirc_init()
        return self

    async def __aexit__(LIRCClient self not None, exc_type, exc_val, exc_tb):
        self.lirc_deinit()

    # Asynchronous Iterator
    def __aiter__(LIRCClient self not None):
        self._ensure_async()
        return aiter_compat(self)

    async def __anext__(LIRCClient self not None):
        while True:
            command = self.lirc_nextcode()
            if command is None:
                asyncio.sleep(self.check_interval)
                continue
            else:
                return command
