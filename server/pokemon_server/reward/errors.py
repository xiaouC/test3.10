class PetExceedError(Exception):
    pass


class MatExceedError(Exception):
    pass


class EquipExceedError(Exception):
    pass


class NotEnoughError(Exception):
    pass


class MatNotEnoughError(NotEnoughError):
    pass


class PetNotEnoughError(NotEnoughError):
    pass


class GemNotEnoughError(NotEnoughError):
    pass


class AttrNotEnoughError(NotEnoughError):
    def __init__(self, message, attr):
        super(AttrNotEnoughError, self).__init__(message % attr)
        self.attr = attr
