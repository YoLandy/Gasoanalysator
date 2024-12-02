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
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic

from basic import BasePage
from utils.datamanager.data import DataManager

import pyqtgraph as pg


class ParamPage(BasePage):
    UI_FILEPATH = "front/parampage.ui"
    _save_param_signal = pyqtSignal(str)
    _update_param_signal = pyqtSignal(str)

    def __init__(self):
        super(ParamPage, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.back_btn.clicked.connect(self.pause)
        self.back_btn.clicked.connect(self.save_before_close)
        self._save_param_signal.connect(self.save_param)
        self._update_param_signal.connect(self.update_param)

        self.param_map = {
            "Naves mass": {
                "sb": self.mass_sb,
                "ok": self.mass_save_btn,
                "cancel": self.mass_cancel_btn,
            },
            "Control exp C": {
                "sb": self.control_exp_C_sb,
                "ok": self.control_exp_C_save_btn,
                "cancel": self.control_exp_C_cancel_btn,
            },
            "Control exp S": {
                "sb": self.control_exp_S_sb,
                "ok": self.control_exp_S_save_btn,
                "cancel": self.control_exp_S_cancel_btn,
            },
            "Koeff C": {
                "sb": self.koeff_C_sb,
                "ok": self.koeff_C_save_btn,
                "cancel": self.koeff_C_cancel_btn,
            },
            "Koeff S": {
                "sb": self.koeff_S_sb,
                "ok": self.koeff_S_save_btn,
                "cancel": self.koeff_S_cancel_btn,
            },
            "Analyse time": {
                "sb": self.time_sb,
                "ok": self.time_save_btn,
                "cancel": self.time_cancel_btn,
            },
        }

        self.C_koeffs = [
            {
                "line": eval(f"self.lineEdit_{i}"),
                "sb": eval(f"self.doubleSpinBox_{i}"),
                "rb": eval(f"self.radioButton_{i}"),
            }
            for i in range(1, 11)
        ]

        self.S_koeffs = [
            {
                "line": eval(f"self.lineEdit_{i}"),
                "sb": eval(f"self.doubleSpinBox_{i}"),
                "rb": eval(f"self.radioButton_{i}"),
            }
            for i in range(11, 21)
        ]

        self.connect_buttons()

        self.set_params()

        self.startup()

    def start(self):
        super().start()
        self.set_params()

    def set_params(self):
        for paramname in self.param_map:
            param = DataManager.get_param(paramname)
            self.param_map[paramname]["sb"].setValue(param)

        koeffs = DataManager.get_param("Choose_koeffs")

        self.set_koeffs_to_lines(koeffs["C"], self.C_koeffs)
        self.set_koeffs_to_lines(koeffs["S"], self.S_koeffs)

    def set_koeffs_to_lines(self, koeffs, koeffs_objs):
        for koeff, koeff_obj in zip(koeffs, koeffs_objs):
            if koeff["key"] and koeff["val"]:
                koeff_obj["line"].setText(koeff["key"])
                koeff_obj["sb"].setValue(koeff["val"])

    def connect_buttons(self):
        for paramname in self.param_map:
            self.param_map[paramname]["ok"].clicked.connect(
                lambda ch, param=paramname: self._save_param_signal.emit(param)
            )
            self.param_map[paramname]["cancel"].clicked.connect(
                lambda ch, param=paramname: self._update_param_signal.emit(param)
            )

    def save_param(self, paramname):
        print("save", paramname)
        DataManager.save_param(paramname, self.param_map[paramname]["sb"].value())
        if paramname in ["Koeff C", "Koeff S"]:
            self.deny_choose(paramname)

    def update_param(self, paramname):
        print("update", paramname)
        self.param_map[paramname]["sb"].setValue(DataManager.get_param(paramname))

    def deny_choose(self, koeff_type):
        koeffs = {"Koeff C": self.C_koeffs, "Koeff S": self.S_koeffs}[koeff_type]

        for koeff in koeffs:
            btn = koeff["rb"]
            btn.setAutoExclusive(False)
            btn.setChecked(False)
            btn.repaint()
            btn.setAutoExclusive(True)

    def save_before_close(self):
        for koeffs, label in zip(
            [self.C_koeffs, self.S_koeffs], ["Koeff C", "Koeff S"]
        ):
            for koeff in koeffs:
                btn = koeff["rb"]
                if btn.isChecked() and (koeff["line"].text() and koeff["sb"]):
                    DataManager.save_param(label, koeff["sb"].value())

                if btn.isChecked() and not (koeff["line"].text() and koeff["sb"]):
                    self.deny_choose(label)

    def closeEvent(self, event):
        self.back_btn.clicked.emit()
        super(BasePage, self).closeEvent(event)
