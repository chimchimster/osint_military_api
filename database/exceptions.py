from enum import Enum


class Signals(Enum):
    SOURCE_ID_EXISTS = 1
    NO_MORE_THAN_ONE_ACCOUNT_FOR_PROFILE = 2

    def __str__(self):
        return f'{self.name}'