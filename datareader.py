import time

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5 import uic

from instruments.gasoanalisator.gashandler import (
    GICommands,
    GIApiStatus,
    GIStatus,
    GIAnswerStatus,
    GasoanalysatorHandler,
)


import pyqtgraph as pg

import sys


class GasReader(QWidget):
    RUDE_COMPORT = "COM7"
    PREC_COMPORT = "COM6"

    status_signal = pyqtSignal(str)
    data_signal = pyqtSignal(dict)

    def __init__(self):
        super(GasReader, self).__init__()
        self.gas_rude = GasoanalysatorHandler(self.RUDE_COMPORT, label="rude")
        time.sleep(0.1)
        self.gas_prec = GasoanalysatorHandler(self.PREC_COMPORT, label="prec")

        self.datacollector = DataCollector()
        self.datacollector.data_good.connect(self.return_data)
        self.datacollector.status_good.connect(self.return_status)

        self.timer = QTimer()

        for gas in [self.gas_rude, self.gas_prec]:
            gas.responce.connect(self.recieve)

        self.command = None
        self.already_zeroing = False

    def get_data(self):
        self.send(GICommands.get_data)

    def return_data(self, data):
        self.data_signal.emit(data)

    def return_status(self, status):
        self.status_signal.emit(status)

    def send(self, command, gas=None):
        self.command = command

        if gas is None:
            for gas_ in [self.gas_rude, self.gas_prec]:
                gas_.send_command(command)
        else:
            gas.send_command(command)

    def zeroing(self):
        self.send(GICommands.set_zero)

    def recieve(self, responce):
        code = responce["code"]
        content = responce["content"]
        gas = self.sender()

        if code == GIApiStatus.error and content == GIAnswerStatus.passive_state:
            self.send(GICommands.set_active, gas)
            return

        if self.command == GICommands.set_active:
            if code == GIApiStatus.status and content == GIStatus.ok:
                self.send(GICommands.get_data, gas)
            else:
                self.status_signal.emit(str(responce) + gas.label)

        if self.command == GICommands.get_data:
            if code == GIApiStatus.data:
                self.datacollector.collect_data(content, gas)

        if self.command == GICommands.set_zero:
            if not self.already_zeroing:
                self.start_status_updating()
                self.already_zeroing = True

        if self.command == GICommands.get_status:
            if code == GIApiStatus.status and content in [
                GIStatus.in_progress,
                GIStatus.started_zero,
            ]:
                self.datacollector.collect_status("zeroing", gas)

            if code == GIApiStatus.status and content == GIStatus.done_zeroing:
                self.datacollector.collect_status("done zeroing", gas)
                self.end_status_updating()

    def start_status_updating(self):
        self.timer.timeout.connect(self.timer_update_slot)
        self.timer.start(1000)

    def end_status_updating(self):
        self.already_zeroing = False
        self.timer.stop()
        self.timer.disconnect()

    def timer_update_slot(self):
        self.send(GICommands.get_status)


class DataCollector(QObject):
    data_good = pyqtSignal(dict)
    status_good = pyqtSignal(str)

    def __init__(self) -> None:
        super(DataCollector, self).__init__()
        self.data_steak = {
            "C": {"1": None, "2": None, "3": None, "4": None},
            "S": {
                "1": None,
                "2": None,
            },
        }
        self.status_income = {"prec": "", "rude": ""}

    def collect_status(self, status, gas):
        self.status_income[gas.label] = status

        if self.status_income["prec"] and self.status_income["rude"]:
            if self.status_income["prec"] != self.status_income["rude"]:
                print("OH NOOOOOO!!!!!!!!!", self.status_income)
            self.status_good.emit(self.status_income["prec"])
            self.status_income = {"prec": "", "rude": ""}

    def collect_data(self, content, sender):
        if sender.label == "prec":
            self.data_steak["C"]["1"] = content["CO"]
            self.data_steak["C"]["2"] = content["CH"]
            self.data_steak["S"]["1"] = content["CO2"]

        if sender.label == "rude":
            self.data_steak["C"]["3"] = content["CO"]
            self.data_steak["C"]["4"] = content["CH"]
            self.data_steak["S"]["2"] = content["CO2"]

        if self.is_full(self.data_steak["C"]) and self.is_full(self.data_steak["S"]):
            self.data_good.emit(self.data_steak)
            self.data_steak = {
                "C": {"1": None, "2": None, "3": None, "4": None},
                "S": {
                    "1": None,
                    "2": None,
                },
            }

    def is_full(self, data):
        return all([not data[name] is None for name in data])

    def is_none(self, data):
        return all([data[name] is None for name in data])
