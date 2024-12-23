import sys
from PyQt5.QtWidgets import (
    QApplication,
)

from pages.mainpage.mainpage import MainWindow
from pages.parampage.parampage import ParamPage
from pages.confirmpage.confirmpage import ConfirmationPage

app = QApplication(sys.argv)

mainpage = MainWindow()
parampage = ParamPage()
confirmpage = ConfirmationPage()

mainpage.params_btn.clicked.connect(parampage.start)
parampage.back_btn.clicked.connect(mainpage.start)

mainpage.show_confirmation_page_signal.connect(confirmpage.startslot)
confirmpage.confirm_succes_signal.connect(mainpage.confirmed_succes)

mainpage.window_closed.connect(parampage.close)
mainpage.window_closed.connect(confirmpage.close)

mainpage.show()

sys.exit(app.exec())
