import os
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5 import uic

from utils.datamanager.data import DataManager
from utils.calculator.calculator import Calculator

from instruments.gasoanalisator.gasreader import GasReader

import pyqtgraph as pg
import time


class MainWindow(QMainWindow):
    show_confirmation_page_signal = pyqtSignal(dict)
    window_closed = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("front/mainwin.ui", self)
        self.graphcells = [self.c_graphcell, self.s_graphcell]
        self.c_graphcell.setup("Углерод", 4, "", Calculator([], "C"))
        self.s_graphcell.setup("Сера", 2, "", Calculator([], "S"))

        self.setWindowTitle('cheSCan 1.0')

        self.timer = QTimer()

        self.gasreader = GasReader()
        self.gasreader.status_signal.connect(self.operate_status)
        self.gasreader.data_signal.connect(self.operate_data)

        self.analysis_btn.clicked.connect(self.start_analysis)
        self.control_exp_btn.clicked.connect(self.start_control_exp)

        self.cancel_btn.clicked.connect(self.stop_ticking)
        self.zero_button.clicked.connect(self.zeroing)
        self.params_btn.clicked.connect(self.pause)

        self.progressBar.setValue(0)
        self.show_confirm = False

        self.start()
        self.showMaximized()

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
            if en == True and btn != self.cancel_btn:
                btn.setStyleSheet('font: 75 16pt "MS Shell Dlg 2";')

    def operate_status(self, status):
        print("status slot")
        if status == "zeroing":
            for graphcell in self.graphcells:
                graphcell.show_zeroing_progress()
        if status == "done zeroing":
            self.enable_interface(True)
            for graphcell in self.graphcells:
                graphcell.show_end_zeroing_progress()

        print(status)

    def operate_data(self, data):
        print("data slot")
        dataC, dataS = data["C"], data["S"]
        self.c_graphcell.add(dataC)
        self.s_graphcell.add(dataS)

    def tick(self):
        if self.progressBar.value() >= self.progressBar.maximum():
            self.stop_ticking()

            for graphcell in self.graphcells:
                graphcell.show_end_conc()

            if self.show_confirm:
                self.enable_interface(False)
                self.show_confirmation_page()
            return

        self.gasreader.get_data()
        self.progressBar.setValue(self.progressBar.value() + 1)

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
        self.c_graphcell.ce = False
        self.analysis_btn.setStyleSheet(
            'font: 75 16pt "MS Shell Dlg 2"; color: rgb(255, 0, 0);'
        )
        self.show_confirm = False
        self.clean()
        self.enable_interface(False)
        self.cancel_btn.setEnabled(True)
        self.start_ticking(DataManager.get_param("Analyse time"))

    def start_control_exp(self):
        self.c_graphcell.ce = True
        self.control_exp_btn.setStyleSheet(
            'font: 75 16pt "MS Shell Dlg 2"; color: rgb(255, 0, 0);'
        )
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
        self.gasreader.zeroing()

    def done_zeroing_slot(self):
        self.enable_interface(True)

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

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
