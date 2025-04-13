import logging

from enums import ErrorType, WarningType

from types import UnionType

ExceptionType: UnionType = ErrorType | WarningType

logging.basicConfig(format='%(levelname)s @ %(asctime)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    level=logging.WARNING)


class Error:

    def __init__(self, status: ExceptionType, message: str = ""):
        self.Status: ExceptionType = status
        self.Message: str = message

    def log(self):
        if type(self.Status) == WarningType:
            logging.warning(f"{self.Status.name}: {self.Message}")
        elif type(self.Status) == ErrorType:
            logging.error(f"{self.Status.name}: {self.Message}")
