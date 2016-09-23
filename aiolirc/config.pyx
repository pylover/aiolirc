
from libc.stdlib cimport calloc, free

from aiolirc.constants import ENCODING
from aiolirc.c_lirc_client cimport lirc_config, lirc_freeconfig, lirc_readconfig, lirc_code2char
from aiolirc.exceptions import LIRCLoadConfigError, TranslateError, TranslateDone, LIRCConfigInitError


cdef int STRING_BUFFER_LEN = 256


cdef class LIRCConfig:
    cdef lirc_config * _c_lirc_config

    def __cinit__(self, config_filename):
        self.add_config_file(config_filename)

    def __dealloc__(self):
        if self._c_lirc_config is not NULL:
            lirc_freeconfig(self._c_lirc_config)

    def add_config_file(LIRCConfig self not None, config_filename):
        if config_filename is not None:
            lirc_readconfig(
                config_filename, &self._c_lirc_config, NULL)
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

    def _ensure_init(LIRCConfig self not None):
        if self._c_lirc_config is NULL:
            raise LIRCConfigInitError('%s has not been initialised.' % self.__name__)
