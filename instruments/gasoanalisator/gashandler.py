from enum import Enum

from PyQt5.QtCore import QObject, QIODevice, pyqtSignal
from PyQt5 import QtSerialPort

from .utils import float_from_bytes
from instruments.instrument import Instrument


class GIAnswerStatus(Enum):
    """
    This enum is for gasoanalysator answer status
    """

    ok = 0x00
    hard_error = 0x01
    later_command = 0x02
    in_progress = 0x03
    unknown_command = 0x04
    invalid_format = 0x05
    invalid_chksm = 0x06
    setting_hard = 0x07
    passive_state = 0x08
    cant_done = 0x09
    unknown_error = 0x0A


class GICommands(Enum):
    """
    This enum is for gasoanalysator commands
    """

    set_zero = b"\x8A\x01\x01\x44\x85\x4b"
    set_active = b"\x8A\x01\x01\x04\x85\x0B"
    get_data = b"\x8A\x01\x01\x43\x85\x4C"
    get_status = b"\x8A\x01\x01\x01\x85\x0E"


GOOD_ANSWER_STATUS = {
    GICommands.set_zero: GIAnswerStatus.later_command,
    GICommands.set_active: GIAnswerStatus.ok,
    GICommands.get_data: GIAnswerStatus.ok,
    GICommands.get_status: GIAnswerStatus.ok,
}


class GIStatus(Enum):
    """
    This enum is for gasoanalysator status
    """

    ok = 0x00
    started_zero = 0x01
    in_progress = 0x02
    done_zeroing = 0x03


class GIApiStatus(Enum):
    """
    API

    {
        'code' : GIApiStatus.data
        'content': ....
    }
    """

    data = 1
    status = 2
    error = 3


class GasoanalysatorHandler(Instrument):
    cls_handlers: dict = {}
    responce = pyqtSignal(dict)

    @staticmethod
    def register_handler(command, handlers=cls_handlers):
        """
        handler registrator for more comfortable usage
        """

        def decorator(handler):
            handlers[command] = handler

        return decorator

    def __init__(self, comport, label="", baudrate=9600):
        super().__init__(comport, baudrate=baudrate)
        self.current_command = None
        self.label = label

    def send_command(self, command: GICommands):
        """
        send command method whih uses GasoanalysatorInstrumentCommands type as input
        """
        print("out", self.serial.portName(), command)

        self.current_command = command
        self.send(command.value)

    def check_buffer(self, buffer):
        # return buffer.startswith(b"\x8A") and buffer.endswith(b"\x85")
        return b"\x8A" in buffer and b"\x85" in buffer

    def predprocess_data(self, buffer):
        data = b"\x8a" + buffer.split(b"\x8a")[-1]
        return data

    def operate_data(self, data):
        status, content = self.parse_buffer(data)

        if not self.status_validation(status):
            answer = self.make_answer(GIApiStatus.error, content=status)
            print("in", self.serial.portName(), answer)
            self.responce.emit(answer)
            return

        answer = self.cls_handlers[self.current_command](self, content)
        print("in", self.serial.portName(), answer)
        self.responce.emit(answer)

    @register_handler(GICommands.get_data)
    def get_data_handler(self, content):
        """
        handler which handles answer on "get data" command
        """
        answer = {}
        for i, paramname in enumerate(["CO", "CH", "CO2", "O2", "NO", "L"]):
            answer[paramname] = int(
                float_from_bytes(content[6 * i : 6 * (i + 1)]) * 10**4
            )

        return self.make_answer(GIApiStatus.data, content=answer)

    @register_handler(GICommands.get_status)
    def get_status_handler(self, content):
        """
        handler which handles "get status" command
        """
        gasoanalysator_status = GIStatus(content[0])
        return self.make_answer(GIApiStatus.status, content=gasoanalysator_status)

    @register_handler(GICommands.set_active)
    def set_active_handler(self, content):
        """
        handler which handles "set_active" command
        """
        return self.make_answer(GIApiStatus.status, GIStatus.ok)

    @register_handler(GICommands.set_zero)
    def get_zero_handler(self, content):
        """
        handler which handles "set_zero" command
        """
        return self.make_answer(GIApiStatus.status, GIStatus.ok)

    def status_validation(self, status: GIAnswerStatus) -> bool:
        """
        Checks if answer status (gasoanal error) is good
        """
        return status == GOOD_ANSWER_STATUS.get(self.current_command)

    def get_answer_status_from_buffer(self, data: bytearray) -> GIAnswerStatus:
        """
        Gets answer status from raw
        """
        return GIAnswerStatus(data[3])

    def get_content_from_buffer(self, data: bytearray) -> bytearray:
        """
        gets content from buffer
        """
        data_len = data[2]
        content = data[4 : 4 + data_len - 1]
        return content

    def parse_buffer(self, data: bytearray) -> tuple:
        """
        Gets bytearray buffer (message) and returnd tuple (status, content)
        """
        return self.get_answer_status_from_buffer(data), self.get_content_from_buffer(
            data
        )

    def make_answer(self, code, content):
        """
        Makes answer by form
        """
        return {"code": code, "content": content}


if __name__ == "__main__":
    pass
