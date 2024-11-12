import os
import sys
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QMainWindow,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5 import uic

from pages.mainpage.mainpage import MainWindow
from pages.parampage.parampage import ParamPage
from pages.confirmpage.confirmpage import ConfirmationPage

import pyqtgraph as pg


def test_slot(aaaa):
    print(aaaa)


app = QApplication(sys.argv)

mainpage = MainWindow()
parampage = ParamPage()
confirmpage = ConfirmationPage()

mainpage.params_btn.clicked.connect(parampage.start)
parampage.back_btn.clicked.connect(mainpage.start)

mainpage.show_confirmation_page_signal.connect(confirmpage.startslot)
confirmpage.confirm_succes_signal.connect(mainpage.confirmed_succes)

mainpage.show()

sys.exit(app.exec())
