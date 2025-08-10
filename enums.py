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


class ModerationType(Enum):
    Mute = 1


class TrackSortType(Enum):
    AlphabeticalAsc = 0
    AlphabeticalDes = 1
    DurationAsc = 2
    DurationDes = 3
