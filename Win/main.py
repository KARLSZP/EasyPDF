# import PyQt5
import os
import sys
from PyQt5.QtWidgets import QApplication
from src.EasyPDF.gui import EasyPDF_GUI
from PyQt5.QtGui import QIcon
from src.EasyPDF.config import Config
import ctypes


if __name__ == '__main__':
    os.chdir(os.path.split(os.path.realpath(sys.argv[0]))[0])
    config = Config("src/config.ini")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(config["gui"]["iconPath"]))

    myappid = 'easyPDF'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    easyPDF = EasyPDF_GUI(config)
    easyPDF.show()
    sys.exit(app.exec_())
