class ResilentException(Exception):
    pass

class UnhandledException(ResilentException):
    pass

class UnsupportedProxyType(ResilentException):
    pass