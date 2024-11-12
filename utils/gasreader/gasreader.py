from PyQt5.QtWidgets import (
    QMainWindow,
)
from PyQt5.QtCore import pyqtSignal, QTimer

import itertools


class GasReader(QMainWindow):
    send_dot_signal = pyqtSignal(dict)
    end_signal = pyqtSignal()

    def __init__(self) -> None:
        super(GasReader, self).__init__()
        self.time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_slot)
        self.dataC = itertools.cycle(
            [1, 2, 3, 5, 8, 12, 17, 16, 12, 10, 6, 5, 4, 3, 2, 1]
        )
        self.dataS = itertools.cycle(
            reversed([1, 2, 3, 5, 8, 12, 17, 16, 12, 10, 6, 5, 4, 3, 2, 1])
        )
        self.i = 0
        self.stop = False

    # slot
    def set_time(self, time):
        self.time = time

    def start_slot(self):
        print("start")
        self.timer.start(1000)
        self.timer.timeout.connect(self.timer_slot)

    def stop_slot(self):
        print("stop")
        self.timer.stop()
        self.timer.timeout.disconnect()
        self.i = 0

    def zero_slot(self):
        pass

    def timer_slot(self):
        if self.i == self.time:
            self.stop_slot()
            self.end_signal.emit()
            return

        self.send_dot_signal.emit({"C": next(self.dataC), "S": next(self.dataS)})
        self.i += 1


"""
class GasReader(QMainWindow):
    ask_data_signal = pyqtSignal(str)
    send_dot_signal = pyqtSignal(float)

    def __init__(self) -> None:
        self.time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_slot)

        self.check = False
        self.is_reading = False
        self.set_zero = False
        self.set_active = False

    def set_time(self, time):
        self.time = time

    def start_slot(self):
        if not self.is_reading:
            self.ask_data_signal.emit('get_data')
            self.check = True

    def stop_slot(self):
        self.timer.stop()
        self.check = False
        self.is_reading = False
        self.set_zero = False
        self.set_active = False

    def zero_slot(self):
        if not self.set_zero and not self.is_reading:
            # Послать сигнал обнуления
            self.ask_data_signal.emit('set_zero')
            self.set_zero = True

    def timer_slot(self):
        self.ask_data_signal.emit('get_data')

    def start_data_reading(self):
        self.time.start()
        self.is_reading = True

    def gas_data_slot(self, data):
        if self.set_active:
            self.check = True
            self.set_active = False
            self.ask_data_signal.emit('get_data')
            return
        
        if self.set_zero:
            print('zero')
            self.set_zero = False
            return
        
        if self.check:
            if 'data' in data:
                self.start_data_reading()
                
            if data == 'not_active':
                self.ask_data_signal.emit('set_active')
                self.set_active = True
            self.check = False
            return
        
        if self.is_reading:
            if not self.time:
                self.timer.stop()
                self.is_reading = False
                return
            
            data = int(data.split(':')[-1])
            self.send_dot_signal.emit(data)

            return
"""
