

class LIRCError(Exception):
    pass


class LIRCInitError(LIRCError):
    pass


class LIRCDeinitError(LIRCError):
    pass


class LIRCAbuseError(LIRCError):
    pass


class LIRCNextCodeError(LIRCError):
    pass


class LIRCConfigError(LIRCError):
    pass


class LIRCLoadConfigError(LIRCConfigError):
    pass


class TranslateError(LIRCConfigError):
    pass


class TranslateDone(LIRCConfigError):
    pass


class LIRCConfigInitError(LIRCConfigError):
    pass
