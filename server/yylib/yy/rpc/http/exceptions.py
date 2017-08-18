# coding: utf-8
class MethodKeyCollide(Exception):
    pass

class ApplicationError(Exception):
    def __init__(self, errcode, errmsg=''):
        self.errcode = errcode
        self.errmsg = errmsg
    def __str__(self):
        return '%05d%s' % (self.errcode, self.errmsg)

class SuspiciousOperation(Exception):
    pass
