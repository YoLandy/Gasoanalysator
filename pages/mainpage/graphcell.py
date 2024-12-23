from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt
from utils.datamanager.data import DataManager
from PyQt5 import uic, QtGui

from config import THRESHOLD

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

        self.calculator = None
        self.title = None
        self.info = ""
        self.n = 0

        b = QtGui.QFont()
        b.setPixelSize(20)

        pen = pg.mkPen(color=(255, 255, 200), width=1)
        self.widget.plotItem.getAxis("left").setPen(pen)
        self.widget.plotItem.getAxis("bottom").setPen(pen)
        self.widget.plotItem.getAxis("left").setTickFont(b)
        self.widget.plotItem.getAxis("bottom").setTickFont(b)
        self.widget.plotItem.setContentsMargins(10, 10, 10, 10)

        self.datas = {}

        self.ce = False

    def setup(self, title, channels_count, info, calculator):
        self.title = title
        self.info = info
        self.title_label.setText(self.title)
        self.info_label.setText(self.info)
        self.calculator = calculator

        self.datas = {str(i): [] for i in range(1, channels_count + 1)}
        self.prettize_plot()

    def add(self, data):
        for name in self.datas:
            self.datas[name].append(data[name])

        i_actual = self.get_actual_i()

        self.widget.clear()

        colors = {"1": "r", "2": "g", "3": "b", "4": "y"}

        for name in self.datas:
            data = self.datas[name]
            if name == i_actual:
                self.widget.plot(data, pen=pg.mkPen(color=(colors[name]), width=5))
            else:
                self.widget.plot(
                    data, pen=pg.mkPen(color=(colors[name]), width=2, style=Qt.DashLine)
                )

        data = self.datas[i_actual]
        print('datalen', len(data))
        self.widget.setXRange(0, len(data))
        
        if not (max(data) == 0 and min(data) == 0):
            self.widget.setYRange(min(data), max(data))

        print(f'resize {min(data), max(data)}')

        self.calculator.set_data(data)
        conc = self.calculator.calc_concentrate_int()
        mass = self.calculator.calc_pure_integral_with_coeff()

        self.combobox.clear()
        if not self.ce:
            self.combobox.addItems([f"{round(conc * 100, 4)}%", f"{round(mass, 4)} мг"])
        else:
            self.combobox.addItems([f"{round(mass, 4)} мг", f"{round(conc * 100, 4)}%"])

    def prettize_plot(self):
        axis = self.widget.getAxis("left")  # or 'bottom' for the x-axis

        # Function to format labels with padding
        def format_label(value, a, b):
            if value == []:
                return value
            if max(value) < 10 and min(value) > -10:
                return [" {:.3f}".format(float(x)) for x in value]
            return [
                "{:>6}".format(int(x)) for x in value
            ]  # Adjust '10' for desired width
            
        # Set the tick labels using a custom function
        axis.tickStrings = format_label
        # Update the plot to reflect the changes
        pg.QtGui.QGuiApplication.processEvents()

    def show_end_conc(self):
        conc = self.calculator.calc_concentrate()
        mass = self.calculator.calc_mass()
        self.combobox.clear()
        if not self.ce:
            self.combobox.addItems([f"{round(conc * 100, 4)}%", f"{round(mass, 4)} мг"])
        else:
            self.combobox.addItems([f"{round(mass, 4)} мг", f"{round(conc * 100, 4)}%"])

    def clean(self):
        self.widget.clear()
        for name in self.datas:
            self.datas[name] = []

    def show_zeroing_progress(self):
        self.n += 1
        self.info_label.setText("В процессе обнуления" + "." * (self.n % 4))

    def show_end_zeroing_progress(self):
        self.info_label.setText("")

    def get_actual_i(self):
        i_actual = max(self.datas.keys())

        for name in sorted(self.datas.keys()):
            data = self.datas[name]
            print(name, max(data), min(data))
            if max(data) < THRESHOLD:
                i_actual = name
                break

        return i_actual