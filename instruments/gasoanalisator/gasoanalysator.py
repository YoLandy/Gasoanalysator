"""
this module is an abstract gasoanalysator handler
"""

import enum
from PyQt5.QtCore import QObject, QIODevice
from PyQt5 import QtSerialPort


class GasStatus(enum.Enum):
    """
    This enum is for gasoanalysator status
    """

    ok = "ok"
    incomplete = 2
    in_progress = "programm in progress"
    in_zeroing = "making zeroing command"
    stopped = 5
    error = 6


class Gasoanalysator(QObject):
    """
    Abstract gas handler
    """

    def __init__(self, gasoanalysator) -> None:
        super().__init__(Gasoanalysator)
        self.gasoanalysator = gasoanalysator
        self.state = GasStatus.ok

    def get_state(self):
        return self.state

    def get_data(self):
        """
        Interface method
        """
        self.state = GasStatus.in_progress

    def start_zeroing(self):
        """
        Interface method
        """
        self.state = GasStatus.in_zeroing
