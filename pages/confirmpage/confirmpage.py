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
    QDesktopWidget,
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

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.rbs = [self.c_save_rb, self.c_cancel_rb, self.s_save_rb, self.s_cancel_rb]

        self.c_save_rb.toggled.connect(self.clicked_slot)
        self.c_cancel_rb.toggled.connect(self.clicked_slot)
        self.s_save_rb.toggled.connect(self.clicked_slot)
        self.s_cancel_rb.toggled.connect(self.clicked_slot)

        self.data = {}

    def clicked_slot(self):
        if len([1 for rb in self.rbs if rb in self.rbs if rb.isChecked()]) == 2:
            self.update_params()
            self.confirm_succes_signal.emit()
            self.end()

    def location_on_the_screen(self):
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = self.geometry()
        x = (ag.width() - widget.width()) // 2

        y = ag.height() - widget.height() - 50
        self.move(x, y)

    def startslot(self, data):
        self.location_on_the_screen()
        self.start()
        self.reset_rbs()
        self.data = data
        self.c_last_value_label.setText(
            f"Старое значение КО по С {round(data['C']['last'], 4)}"
        )
        self.c_current_value_label.setText(
            f"Измеренное значение КО по С {round(data['C']['actual'], 4)}"
        )

        self.s_last_value_label.setText(
            f"Старое значение КО по S {round(data['S']['last'], 4)}"
        )
        self.s_current_value_label.setText(
            f"Измеренное значение КО по S {round(data['S']['actual'], 4)}"
        )

    def update_params(self):
        if self.c_save_rb.isChecked():
            print("change c")
            last, actual = self.data["C"]["last"], self.data["C"]["actual"]
            DataManager.save_param("Control exp C", (last + actual) / 2)
        if self.s_save_rb.isChecked():
            print("change s")
            last, actual = self.data["S"]["last"], self.data["S"]["actual"]
            DataManager.save_param("Control exp S", (last + actual) / 2)

    def reset_rbs(self):
        for rb in self.rbs:
            rb.setAutoExclusive(False)
            rb.setChecked(False)
            rb.repaint()
            rb.setAutoExclusive(True)

    def end(self):
        self.pause()

    def closeEvent(self, event):
        self.confirm_succes_signal.emit()
        self.end()
        super(BasePage, self).closeEvent(event)
