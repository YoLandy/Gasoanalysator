from PyQt5.QtCore import QObject, QIODevice
from PyQt5 import QtSerialPort


class Instrument(QObject):
    """
    Abstract class for Instruments
    """

    def __init__(self, comport, baudrate=9600):
        super(Instrument, self).__init__()

        # ser = serial.Serial(self.COM_PORT, self.BAUDRATE)
        # print(ser.name)
        # ser.close()

        self.serial = QtSerialPort.QSerialPort(
            comport,
            baudRate=baudrate,
            readyRead=self.recieve,
        )
        self.is_open = self.serial.open(QIODevice.ReadWrite)
        print(self.is_open)

        self.need_bytes = 0
        self.buffer = b""
        self.signals = None

    def recieve(self):
        """
        Async method that runs every time when data recieving
        """
        data = self.serial.readAll()
        self.buffer += bytearray(data)

        if self.check_buffer(self.buffer):
            data = self.predprocess_data(self.buffer)
            print(data)
            self.operate_data(data)
            self.buffer = b""

    def send(self, data):
        """
        send data by serial mehtod
        """
        self.serial.write(data)

    def check_buffer(self, buffer):
        """
        Interface method which decide operate data in buffer or not
        """

    def predprocess_data(self, buffer):
        """
        Interface method which predprocess data
        """
        return buffer

    def operate_data(self, data):
        """
        Interface method which operates data in buffer
        """

    def closeEvent(self, event):
        self.serial.close()
        super(QObject, self).closeEvent(event)
