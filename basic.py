import os
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QMainWindow,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5 import uic


class BasePage(QMainWindow):
    UI_FILEPATH = ""
    MAIN_STYLESHEET = ""

    def __init__(self) -> None:
        super(BasePage, self).__init__()
        uic.loadUi(self.UI_FILEPATH, self)

    def startup(self):
        self.setStyleSheet(self.MAIN_STYLESHEET)

    def start(self):
        self.show()

    def pause(self):
        self.hide()
