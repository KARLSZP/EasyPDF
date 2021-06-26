#! /usr/bin/python

import PyQt5
import sys
from PyQt5.QtWidgets import QApplication
from src.EasyPDF.gui import EasyPDF_GUI
from src.EasyPDF.config import Config

if __name__ == '__main__':
    config = Config("src/config.ini")
    app = QApplication(sys.argv)
    easyPDF = EasyPDF_GUI(config)
    easyPDF.show()
    sys.exit(app.exec_())
