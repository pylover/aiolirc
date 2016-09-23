
cdef class LIRCClient(object):
    cdef:
        public unicode lircrc_file, lircrc_prog
        public float check_interval
        public bint verbose, _blocking
        public object _loop
        public int _lirc_socket

        void load_config_file(LIRCClient self, unicode lircrc_file)
        void update_blocking(LIRCClient self)
        void lirc_init(LIRCClient self)
        void lirc_deinit(LIRCClient self)
        unicode lirc_nextcode(LIRCClient self)
