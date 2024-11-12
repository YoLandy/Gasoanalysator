from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5 import uic

from instruments.gasoanalisator.gashandler import (
    GICommands,
    GIApiStatus,
    GIStatus,
    GIAnswerStatus,
)


import pyqtgraph as pg

import sys


class GraphCell(QWidget):
    done_zeroing = pyqtSignal()

    def __init__(self, parent):
        super(GraphCell, self).__init__(parent)
        uic.loadUi("front/graphcell.ui", self)
        self.gas = None
        self.calculator = None
        self.title = None
        self.info = ""
        self.command = None

        self.channel_i = 0
        self.channel_labels = ["CO", "CH", "CO2", "O2"]
        self.datas = {channel_label: [] for channel_label in self.channel_labels}

        self.n = 0

    def setup(self, gas, title, info, calculator):
        self.gas = gas
        self.title = title
        self.info = info
        self.title_label.setText(self.title)
        self.info_label.setText(self.info)
        self.gas.responce.connect(self.recieve)
        self.timer = QTimer()
        self.calculator = calculator

    def send(self, command):
        self.command = command
        self.gas.send_command(command)

    def recieve(self, responce):
        code = responce["code"]
        content = responce["content"]

        if code == GIApiStatus.error and content == GIAnswerStatus.passive_state:
            self.send(GICommands.set_active)
            return

        if self.command == GICommands.set_active:
            if code == GIApiStatus.status and content == GIStatus.ok:
                self.send(GICommands.get_data)
            else:
                self.status_signal.emit(responce)

        if self.command == GICommands.get_data:
            if code == GIApiStatus.data:
                self.process_data_dot(responce)

        if self.command == GICommands.set_zero:
            self.show_zeroing_progress()
            self.start_status_updating()

        if self.command == GICommands.get_status:
            if code == GIApiStatus.status and content in [
                GIStatus.in_progress,
                GIStatus.started_zero,
            ]:
                self.show_zeroing_progress()
            if code == GIApiStatus.status and content == GIStatus.done_zeroing:
                print("emiting done zeroing")
                self.done_zeroing.emit()
                self.show_end_zeroing_progress()
                self.end_status_updating()

    def process_data_dot(self, responce):

        for channel_name in self.datas:
            self.datas[channel_name].append(responce["content"][channel_name])

        if self.channel_i < 3:
            current_channel_name = self.channel_labels[self.channel_i]
            if responce["content"][current_channel_name] > 7000:
                self.channel_i += 1

        current_channel_name = self.channel_labels[self.channel_i]
        data = self.datas[current_channel_name]

        self.widget.clear()
        self.widget.plot(data)
        self.calculator.set_data(data)
        conc = self.calculator.calc_concentrate_int()
        self.info_label.setText(f"конц: {round(conc * 100, 4)}%")

    def show_end_conc(self):
        conc = self.calculator.calc_concentrate()
        self.info_label.setText(f"конц: {round(conc * 100, 4)}%")

    def clean(self):
        self.widget.clear()
        for name in self.datas:
            self.datas[name] = []

    def tick(self):
        self.send(GICommands.get_data)

    def zeroing(self):
        self.send(GICommands.set_zero)

    def show_zeroing_progress(self):
        self.n += 1
        self.info_label.setText("В процессе обнуления" + "." * (self.n % 4))

    def show_end_zeroing_progress(self):
        self.info_label.setText("")

    def start_status_updating(self):
        self.timer.timeout.connect(self.timer_update_slot)
        self.timer.start(1000)

    def end_status_updating(self):
        self.timer.stop()
        self.timer.disconnect()

    def timer_update_slot(self):
        self.send(GICommands.get_status)
