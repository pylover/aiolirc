
from aiolirc.c_lirc_client cimport lirc_config

cdef class LIRCConfig:
    cdef:
        lirc_config * _c_lirc_config
        public unicode translate(LIRCConfig self, char * code)


cdef class LIRCClient(object):
    cdef:
        public unicode lircrc_file, lircrc_prog
        public float check_interval
        public bint verbose, _blocking
        public object _loop
        int _lirc_socket

        void load_config_file(LIRCClient self, unicode lircrc_file)
        void update_blocking(LIRCClient self)
        void lirc_init(LIRCClient self)
        void lirc_deinit(LIRCClient self)
        unicode lirc_nextcode(LIRCClient self)
