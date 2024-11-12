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

from instruments.gasoanalisator.gashandler import GasoanalysatorHandler
from datareader import GasReader

import pyqtgraph as pg
import time


class MainWindow(QMainWindow):
    show_confirmation_page_signal = pyqtSignal(dict)

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("front/mainwin.ui", self)
        self.graphcells = [self.c_graphcell, self.s_graphcell]

        self.analysis_btn.clicked.connect(self.start_analysis)
        self.control_exp_btn.clicked.connect(self.start_control_exp)
        self.timer = QTimer()

        self.c_graphcell.setup(
            GasoanalysatorHandler("COM6"), "График углерода", "", Calculator([], "C")
        )
        time.sleep(0.1)
        self.s_graphcell.setup(
            GasoanalysatorHandler("COM7"), "График серы", "", Calculator([], "S")
        )

        self.cancel_btn.clicked.connect(self.stop_ticking)
        self.zero_button.clicked.connect(self.zeroing)

        self.params_btn.clicked.connect(self.pause)

        for graphcell in self.graphcells:
            graphcell.done_zeroing.connect(self.done_zeroing_slot)

        self.all_zero = 0

        self.progressBar.setValue(0)

        self.start()
        self.show_confirm = False
        self.show()

    def pause(self):
        self.enable_interface(False)

    def start(self):
        self.set_mass()
        self.set_time()
        self.enable_interface(True)

    def confirmed_succes(self):
        pass

    def enable_interface(self, en):
        for btn in [
            self.analysis_btn,
            self.control_exp_btn,
            self.cancel_btn,
            self.zero_button,
            self.params_btn,
        ]:
            btn.setEnabled(en)

    def tick(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

        if self.progressBar.value() >= self.progressBar.maximum():
            self.stop_ticking()

            for graphcell in self.graphcells:
                graphcell.show_end_conc()

            if self.show_confirm:
                self.enable_interface(False)
                self.show_confirmation_page()
            return

        for graphcell in self.graphcells:
            graphcell.tick()

    def show_confirmation_page(self):
        self.show_confirmation_page_signal.emit(
            {
                "C": {
                    "last": DataManager.get_param("Control exp C"),
                    "actual": self.c_graphcell.calculator.calc_mass(),
                },
                "S": {
                    "last": DataManager.get_param("Control exp S"),
                    "actual": self.s_graphcell.calculator.calc_mass(),
                },
            }
        )

    def confirmed_succes(self):
        self.enable_interface(True)
        self.start()

    def clean(self):
        for graphcell in self.graphcells:
            graphcell.clean()

    def start_analysis(self):
        self.show_confirm = False
        self.clean()
        self.enable_interface(False)
        self.cancel_btn.setEnabled(True)
        self.start_ticking(DataManager.get_param("Analyse time"))

    def start_control_exp(self):
        self.show_confirm = True
        self.clean()
        self.enable_interface(False)
        self.cancel_btn.setEnabled(True)
        self.start_ticking(DataManager.get_param("Analyse time"))

    def start_ticking(self, time):
        self.progressBar.setMaximum(time)
        self.progressBar.setValue(0)
        self.timer.start(1000)
        self.timer.timeout.connect(self.tick)

    def stop_ticking(self):
        self.enable_interface(True)
        self.timer.stop()
        self.timer.disconnect()

    def zeroing(self):
        self.enable_interface(False)
        for graphcell in self.graphcells:
            graphcell.zeroing()

    def done_zeroing_slot(self):
        self.all_zero += 1

        if self.all_zero == 2:
            self.enable_interface(True)
            self.all_zero = 0

    def set_time(self):
        time = DataManager.get_param("Analyse time")
        print(time)
        self.show_time(time)

    def set_mass(self):
        mass = DataManager.get_param("Naves mass")
        self.show_mass(mass)

    def mass_slot(self):
        pass

    def show_mass(self, mass):
        self.mass_label.setText(f"Масса навески, мг {mass}")

    def show_time(self, time):
        self.time_label.setText(f"Время анализа, c {time}")
