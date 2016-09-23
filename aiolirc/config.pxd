
from aiolirc.c_lirc_client cimport lirc_config

cdef class LIRCConfig:
    cdef lirc_config * _c_lirc_config
    cdef public unicode translate(LIRCConfig self, char * code)
