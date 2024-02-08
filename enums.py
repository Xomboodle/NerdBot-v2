from enum import Enum


class Claimable(Enum):
    Coin = 0
    Clam = 1


class ErrorType(Enum):
    NoError = 0
    InvalidArgument = 1
    MySqlException = 2


class WarningType(Enum):
    NoWarning = 0
    BadConnection = 1
