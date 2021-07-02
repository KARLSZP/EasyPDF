#! /usr/bin/python

import PyQt5
import os
import sys
from PyQt5.QtWidgets import QApplication
from src.EasyPDF.gui import EasyPDF_GUI
from src.EasyPDF.config import Config
from PyQt5.QtGui import QIcon

if __name__ == '__main__':
    os.chdir(os.path.split(os.path.realpath(sys.argv[0]))[0])
    config = Config("src/config.ini")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(config["gui"]["iconPath"]))

    easyPDF = EasyPDF_GUI(config)
    easyPDF.show()
    sys.exit(app.exec_())
