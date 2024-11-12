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

from basic import BasePage
from utils.datamanager.data import DataManager
from utils.calculator.calculator import Calculator

import pyqtgraph as pg


class ConfirmationPage(BasePage):
    UI_FILEPATH = "front/confirmmain.ui"
    confirm_succes_signal = pyqtSignal()

    def __init__(self):
        super(ConfirmationPage, self).__init__()
        self.c_save_btn.clicked.connect(
            lambda ch, flagname="c", flagval=True: self.clicked_slot(flagname, flagval)
        )
        self.c_cancel_btn.clicked.connect(
            lambda ch, flagname="c", flagval=False: self.clicked_slot(flagname, flagval)
        )
        self.s_save_btn.clicked.connect(
            lambda ch, flagname="s", flagval=True: self.clicked_slot(flagname, flagval)
        )
        self.s_cancel_btn.clicked.connect(
            lambda ch, flagname="s", flagval=False: self.clicked_slot(flagname, flagval)
        )

        self.c_save = False
        self.s_save = False

        self.c_mass = 0
        self.s_mass = 0

        self.decision_c = False
        self.decision_s = False

        self.flags = {"c": self.c_save, "s": self.s_save}

        self.decisions = {"c": self.decision_c, "s": self.decision_s}

        self.data = {}

    def clicked_slot(self, flagname, flagval):
        print(flagname, flagval)
        self.flags[flagname] = flagval

        if flagname == "c":
            self.decision_c = True

        if flagname == "s":
            self.decision_s = True

        print(self.decision_s, self.decision_c)

        if self.decision_s and self.decision_c:
            self.update_params()
            self.confirm_succes_signal.emit()
            self.end()

    def startslot(self, data):
        self.start()
        self.data = data
        self.c_last_value_label.setText(f"Старое значение КО по С {data['C']['last']}")
        self.c_current_value_label.setText(
            f"Измеренное значение КО по С {data['C']['actual']}"
        )

        self.s_last_value_label.setText(f"Старое значение КО по S {data['S']['last']}")
        self.s_current_value_label.setText(
            f"Измеренное значение КО по S {data['S']['actual']}"
        )

    def update_params(self):
        if self.c_save:
            last, actual = self.data["C"]["last"] + self.data["C"]["actual"]
            DataManager.set_param((last + actual) / 2)
        if self.s_save:
            last, actual = self.data["S"]["last"] + self.data["S"]["actual"]
            DataManager.set_param((last + actual) / 2)

    def end(self):
        self.pause()

    def closeEvent(self, event):
        self.confirm_succes_signal.emit()
        self.end()
        super(BasePage, self).closeEvent(event)
