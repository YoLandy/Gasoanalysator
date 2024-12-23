import time

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5 import uic


import pyqtgraph as pg

import sys


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
