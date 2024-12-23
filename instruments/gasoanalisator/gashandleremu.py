from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from enum import Enum
import random

from itertools import cycle

from .gas_instrument_constants import GICommands, GIAnswerStatus, GIApiStatus, GIStatus

GOOD_ANSWER_STATUS = {
   GICommands.get_data: GIAnswerStatus.ok,
   GICommands.get_status: GIAnswerStatus.ok,
   GICommands.set_active: GIAnswerStatus.ok,
   GICommands.set_zero: GIAnswerStatus.ok
}

class GasoanalysatorHandlerEmu(QObject):
    responce = pyqtSignal(dict)  # Сигнал для отправки ответов
    cls_handlers = {}
    def __init__(self, label="Emulator", parent=None):
        super().__init__(parent)
        self.label = label
        self.current_command = None
        self.timer = QTimer()  # Используем таймер для имитации задержек

        self.timer.timeout.connect(self.process_command)
        self.timer.setSingleShot(True)  # Выполнять таймер только один раз
        self.output_data = cycle([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000])  # Имитация получаемых значений
    
    def register_handler(command, handlers = cls_handlers):
          """handler registrator for more comfortable usage"""
          def decorator(handler):
                handlers[command] = handler
          return decorator

    def send_command(self, command: GICommands):
        """Имитирует отправку команды газоанализатору."""
        print(f"Emulator {self.label}: Received command: {command}")
        self.current_command = command
        self.timer.start(random.randint(100, 500)) # Задержка в миллисекундах

    def process_command(self):
        """Имитирует получение и обработку ответа от газоанализатора."""
        if self.current_command is None:
            return

        if self.current_command in self.cls_handlers:
            handler = self.cls_handlers[self.current_command]
            answer = handler(self)
        else:
            answer = self.make_answer(GIApiStatus.error, content="Unknown command")

        print(f"Emulator {self.label}: Sending response: {answer}")
        self.responce.emit(answer)
        self.current_command = None

    def check_buffer(self, buffer):
        # return buffer.startswith(b"\x8A") and buffer.endswith(b"\x85")
        return b"\x8A" in buffer and b"\x85" in buffer

    def predprocess_data(self, buffer):
        data = b"\x8a" + buffer.split(b"\x8a")[-1]
        return data
    
    def make_answer(self, code, content):
        """Makes answer by form"""
        return {"code": code, "content": content}
    
    @register_handler(GICommands.get_data)
    def get_data_handler(self):
      """
      handler which handles answer on "get data" command
      """
      answer = {}
      for paramname in ["CO", "CH", "CO2", "O2", "NO", "L"]:
          #answer[paramname] = random.randint(0, 10000)
          answer[paramname] = next(self.output_data)
          
      return self.make_answer(GIApiStatus.data, content=answer)

    @register_handler(GICommands.get_status)
    def get_status_handler(self):
        """
        handler which handles "get status" command
        """
        gasoanalysator_status = random.choice(list(GIStatus))
        return self.make_answer(GIApiStatus.status, content=gasoanalysator_status)

    @register_handler(GICommands.set_active)
    def set_active_handler(self):
        """
        handler which handles "set_active" command
        """
        return self.make_answer(GIApiStatus.status, content=GIStatus.ok)

    @register_handler(GICommands.set_zero)
    def get_zero_handler(self):
       """
       handler which handles "set_zero" command
       """
       return self.make_answer(GIApiStatus.status, content=GIStatus.ok)
