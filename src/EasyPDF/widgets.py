from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.QtGui import QIntValidator, QStandardItem, QStandardItemModel
import qpageview
import qpageview.viewactions
import re


class Viewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.buildWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.viewArea)
        layout.addWidget(self.controller)
        self.setLayout(layout)

    def buildWidget(self):
        self.viewArea = qpageview.View()
        self.controller = QWidget()
        controllerLayout = QGridLayout()
        previousPageButton = QPushButton("<< previous")
        previousPageButton.setAutoDefault(False)
        previousPageButton.setToolTip('Go to previous page')
        previousPageButton.clicked.connect(self.viewArea.gotoPreviousPage)

        self.pageSelectTextBox = QLineEdit("1")
        self.pageSelectTextBox.setFixedWidth(30)
        self.pageSelectTextBox.setValidator(QIntValidator())
        self.pageSelectTextBox.editingFinished.connect(self.gotoCertainPage)

        self.pageNumsLabel = QLabel(" / NaN")

        nextPageButton = QPushButton("next >>")
        nextPageButton.setAutoDefault(False)
        nextPageButton.setToolTip('Go to next page')
        nextPageButton.clicked.connect(self.viewArea.gotoNextPage)

        controllerLayout.addWidget(previousPageButton, 0, 0)
        controllerLayout.addWidget(
            self.pageSelectTextBox, 0, 1, Qt.AlignRight)
        controllerLayout.addWidget(self.pageNumsLabel, 0, 2, Qt.AlignLeft)
        controllerLayout.addWidget(nextPageButton, 0, 3)

        self.controller.setLayout(controllerLayout)

    def loadFile(self, pdfStream, numPages):
        self.viewArea.loadPdf(pdfStream)
        self.viewArea.setViewMode(qpageview.FitBoth)
        self.viewArea.setViewMode(qpageview.FixedScale)
        self.pageSelectTextBox.setText("1")
        self.pageNumsLabel.setText(" / " + str(numPages))

    @pyqtSlot()
    def gotoCertainPage(self):
        if self.pageSelectTextBox.text():
            self.viewArea.setCurrentPageNumber(
                int(self.pageSelectTextBox.text()))
        else:
            self.pageSelectTextBox.setText(
                str(self.viewArea.currentPageNumber()))


class FileSelector(QWidget):

    fileSelectedSignal = pyqtSignal()
    currentFileSetSignal = pyqtSignal()
    fileSavedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.currentFile = None
        self.fileNames = []
        self.initUI()

    def initUI(self):
        self.buildWidgets()

        layout = QGridLayout()
        layout.addWidget(self.filesSelectLabel, 0, 0)
        layout.addWidget(self.filesSelectButton, 0, 1)
        layout.addWidget(self.currentFileLabel, 1, 0)
        layout.addWidget(self.currentFileComboBox, 1, 1)
        layout.addWidget(self.saveFileLabel, 2, 0)
        layout.addWidget(self.saveFileButton, 2, 1)

        layout.setRowStretch(0, 1)
        # layout.setColumnStretch(0, 1)

        self.setLayout(layout)

    def buildWidgets(self):
        # file(s) selection
        self.filesSelectButton = QPushButton("Select File(s)")
        self.filesSelectButton.setAutoDefault(False)
        self.filesSelectButton.setToolTip('Click to select file(s)')
        self.filesSelectButton.clicked.connect(self.onClickFilesSelect)
        # TODO: finish drop behavior
        # self.filesSelectButton.setAcceptDrops(True)

        self.filesSelectLabel = QLabel("&Select file(s):")
        self.filesSelectLabel.setBuddy(self.filesSelectButton)

        # current file selection
        self.currentFileComboBox = QComboBox()
        self.currentFileComboBox.setSizeAdjustPolicy(
            QComboBox.AdjustToContents)
        self.currentFileComboBox.activated[str].connect(self.setCurrentFile)

        self.currentFileLabel = QLabel("&Current file:")
        self.currentFileLabel.setBuddy(self.currentFileComboBox)

        # save current file
        self.saveFileButton = QPushButton("Save")
        self.saveFileButton.setAutoDefault(False)
        self.saveFileButton.setToolTip('Click to select file(s)')
        self.saveFileButton.clicked.connect(self.onClickSave)

        self.saveFileLabel = QLabel("&Save file:")
        self.saveFileLabel.setBuddy(self.saveFileButton)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "", "PDF Files (*.pdf)", options=options)
        # fileNames, _ = QFileDialog.getOpenFileNames(
        #     self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;Python Files (*.py)", options=options)
        if fileNames:
            print(fileNames)
        return fileNames

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()", "", "PDF Files (*.pdf)", options=options)
        if fileName:
            print(fileName)
        return fileName

    def setCurrentFile(self, text):
        self.currentFile = text
        self.currentFileSetSignal.emit()

    def getCurrentFile(self):
        return self.currentFile

    def getFileNames(self):
        return self.fileNames

    def getSaveFileName(self):
        return self.fileName

    @pyqtSlot()
    def onClickFilesSelect(self):
        self.fileNames = self.openFileNamesDialog()
        if len(self.fileNames) > 0:
            self.currentFileComboBox.clear()
            self.currentFileComboBox.addItems(self.fileNames)
        self.fileSelectedSignal.emit()

    @pyqtSlot()
    def onClickSave(self):
        self.fileName = self.saveFileDialog()
        self.fileSavedSignal.emit()


class PageMerger(QWidget):

    mergeSignal = pyqtSignal()
    resetSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.strategy = 2
        self.margin = 10
        self.initUI()

    def initUI(self):
        self.buildWidgets()

        layout = QGridLayout()
        layout.addWidget(self.strategyLabel, 0, 0)
        layout.addWidget(self.strategySelectComboBox, 0, 1)
        layout.addWidget(self.marginLabel, 1, 0)
        layout.addWidget(self.marginTextBox, 1, 1)
        layout.addWidget(self.pageMergeButton, 2, 0)
        layout.addWidget(self.resetFilesButton, 2, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)

    def buildWidgets(self):
        self.strategySelectComboBox = QComboBox()
        self.strategySelectComboBox.addItems(["2 in 1", "4 in 1", "6 in 1"])
        self.strategySelectComboBox.activated[str].connect(self.setStrategy)

        self.strategyLabel = QLabel("&Strategy:")
        self.strategyLabel.setBuddy(self.strategySelectComboBox)

        self.marginTextBox = QLineEdit("10")
        self.marginTextBox.setValidator(QIntValidator(1, 50))
        self.marginTextBox.editingFinished.connect(self.setMargin)
        self.marginLabel = QLabel("&Margin (1-50):")
        self.marginLabel.setBuddy(self.marginTextBox)

        self.pageMergeButton = QPushButton("Merge Pages")
        self.pageMergeButton.setAutoDefault(False)
        self.pageMergeButton.setToolTip('Click to merge pages')
        self.pageMergeButton.clicked.connect(self.onClickMerge)

        self.resetFilesButton = QPushButton("Reset File(s)")
        self.resetFilesButton.setAutoDefault(False)
        self.resetFilesButton.setToolTip('Click to reset')
        self.resetFilesButton.clicked.connect(self.onClickResetFiles)

    def setStrategy(self, strategy):
        self.strategy = int(strategy.split()[0])
        print(self.strategy)

    def getMergeConfig(self):
        return self.strategy, self.margin

    @pyqtSlot()
    def setMargin(self):
        print(self.marginTextBox.text())
        if self.marginTextBox.text():
            self.margin = int(self.marginTextBox.text())
        else:
            self.margin = 10
            self.marginTextBox.setText("10")

    @pyqtSlot()
    def onClickMerge(self):
        self.mergeSignal.emit()

    @pyqtSlot()
    def onClickResetFiles(self):
        self.resetSignal.emit()
        # self.engine.resetFiles()
        # bytesPDF = self.engine.getDisplayedFile()
        # numPages = self.engine.getCurrentFile().getNumPages()
        # self.viewer.loadFile(bytesPDF, numPages)


class PageScaler(QWidget):

    scaleSignal = pyqtSignal()
    resetSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.selectedPages = []
        self.initUI()

    def initUI(self):
        self.buildWidgets()

        layout = QGridLayout()
        layout.addWidget(self.pagesSelectionLabel, 0, 0)
        layout.addWidget(self.pagesSelectionTextBox, 0, 1)
        layout.addWidget(self.scaleRateSlider, 1, 0)
        layout.addWidget(self.scaleRateTextBox, 1, 1)
        layout.addWidget(self.scalePagesButton, 2, 0)
        layout.addWidget(self.resetFilesButton, 2, 1)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def buildWidgets(self):
        self.scaleRateSlider = QSlider(Qt.Horizontal)
        self.scaleRateSlider.setValue(100)
        self.scaleRateSlider.setRange(10, 500)
        self.scaleRateSlider.setPageStep(5)
        self.scaleRateSlider.valueChanged.connect(self.sliderSetScaleRate)

        self.scaleRateTextBox = QLineEdit("100")
        # scaleRateTextBox.setFixedWidth(30)
        self.scaleRateTextBox.setValidator(QIntValidator())
        self.scaleRateTextBox.editingFinished.connect(self.textBoxSetScaleRate)

        self.pagesSelectionTextBox = QLineEdit("")
        self.pagesSelectionTextBox.editingFinished.connect(self.selectPages)
        self.pagesSelectionLabel = QLabel("&Select Page(s):")
        self.pagesSelectionLabel.setBuddy(self.pagesSelectionTextBox)

        self.scalePagesButton = QPushButton("Scale Pages")
        self.scalePagesButton.setAutoDefault(False)
        self.scalePagesButton.setToolTip('Click to scale selected pages')
        self.scalePagesButton.clicked.connect(self.onClickScale)

        self.resetFilesButton = QPushButton("Reset File(s)")
        self.resetFilesButton.setAutoDefault(False)
        self.resetFilesButton.setToolTip('Click to reset')
        self.resetFilesButton.clicked.connect(self.onClickResetFiles)

        self.extractPagesButton = QPushButton("Extract Pages")

    def setPagesSelection(self, text):
        self.pagesSelectionTextBox.setText(text)
        self.selectPages()

    def getSelectedPages(self):
        return self.selectedPages

    def getScaleRate(self):
        return int(self.scaleRateTextBox.text()) / 100

    @pyqtSlot()
    def selectPages(self):
        pages = self.pagesSelectionTextBox.text()
        # parse pages，
        # legal format: [1], [1-2]
        if pages:
            pages = [s.strip() for s in pages.split(",")]
            selectedPages = set()
            for page in pages:
                if page.isdigit() and int(page) > 0:
                    selectedPages.add(int(page))
                elif re.search(r"^[0-9]+(\s?)+-(\s?)+[0-9]+$", page):
                    for i in range(int(page[:page.find("-")]),
                                   int(page[page.find("-") + 1:]) + 1):
                        selectedPages.add(i)
            print(selectedPages)
        self.selectedPages = sorted(selectedPages)
        # self.selectedPages = sorted([
        # i for i in selectedPages if i <= self.pageReader.getNumPages()])

    @pyqtSlot()
    def sliderSetScaleRate(self):
        self.scaleRateTextBox.setText(str(self.scaleRateSlider.value()))

    @pyqtSlot()
    def textBoxSetScaleRate(self):
        if int(self.scaleRateTextBox.text()) in range(10, 501):
            self.scaleRateSlider.setValue(int(self.scaleRateTextBox.text()))
        else:
            self.scaleRateTextBox.setText("100")
            self.scaleRateSlider.setValue(100)

    @pyqtSlot()
    def onClickScale(self):
        self.scaleSignal.emit()

    @pyqtSlot()
    def onClickResetFiles(self):
        self.resetSignal.emit()


class PageSplitter(QWidget):
    splitSignal = pyqtSignal()
    AverageMode = 0
    AssignedMode = 1
    ExtractingMode = 2

    def __init__(self):
        super().__init__()
        self.selectedPages = [1]
        self.selectedGroups = [[1]]
        self.strategy = self.AverageMode
        self.initUI()

    def initUI(self):
        self.buildWidgets()

        layout = QGridLayout()
        layout.addWidget(self.strategyComboBox, 0, 0)
        layout.addWidget(self.pagesSelectionTextBox, 0, 1)
        layout.addWidget(self.helpMsgButton, 1, 0, 1, 2)
        layout.addWidget(self.splitPagesButton, 2, 0)
        layout.addWidget(self.extractPagesButton, 2, 1)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def buildWidgets(self):

        self.strategyComboBox = QComboBox()
        self.strategyComboBox.addItems(
            ["Average Page", "Assigned Pages", "Extract Pages"])
        self.strategyComboBox.setSizeAdjustPolicy(
            QComboBox.AdjustToContents)
        self.strategyComboBox.activated[str].connect(self.setStrategy)

        self.helpMsgButton = QPushButton("Help")
        self.helpMsgButton.setAutoDefault(False)
        self.helpMsgButton.setToolTip('Click to get detailed info.')
        self.helpMsgButton.clicked.connect(self.showHelpMsg)

        self.pagesSelectionTextBox = QLineEdit("1")
        self.pagesSelectionTextBox.editingFinished.connect(self.selectPages)

        self.splitPagesButton = QPushButton("Split Pages")
        self.splitPagesButton.setAutoDefault(False)
        self.splitPagesButton.setToolTip('Click to split file')
        self.splitPagesButton.clicked.connect(self.onClickSplit)

        self.extractPagesButton = QPushButton("Extract Pages")
        self.extractPagesButton.setAutoDefault(False)
        self.extractPagesButton.setDisabled(True)
        self.extractPagesButton.setToolTip('Click to extract file')
        self.extractPagesButton.clicked.connect(self.onClickSplit)

    def setStrategy(self, text):
        if text == "Average Page":
            self.strategy = self.AverageMode
            self.splitPagesButton.setDisabled(False)
            self.extractPagesButton.setDisabled(True)

        elif text == "Assigned Pages":
            self.strategy = self.AssignedMode
            self.splitPagesButton.setDisabled(False)
            self.extractPagesButton.setDisabled(True)

        elif text == "Extract Pages":
            self.strategy = self.ExtractingMode
            self.pagesSelectionTextBox.setText("1-1")
            self.extractPagesButton.setDisabled(False)
            self.splitPagesButton.setDisabled(True)

    def setPagesSelection(self, text):
        self.pagesSelectionTextBox.setText(text)
        self.selectPages()

    def getStrategy(self):
        return self.strategy

    def getSelectedPages(self):
        return self.selectedPages

    def getSelectedGroups(self):
        return self.selectedGroups

    @pyqtSlot()
    def selectPages(self):
        self.selectedGroups = []
        pages = self.pagesSelectionTextBox.text()
        # parse pages，
        # legal format: [1], [1-2]
        if pages:
            pages = [s.strip() for s in pages.split(",")]
            selectedPages = set()
            for page in pages:
                if page.isdigit() and int(page) > 0:
                    selectedPages.add(int(page))
                    self.selectedGroups.append([int(page)])
                elif re.search(r"^[0-9]+(\s?)+-(\s?)+[0-9]+$", page):
                    self.selectedGroups.append([])
                    for i in range(int(page[:page.find("-")]),
                                   int(page[page.find("-") + 1:]) + 1):
                        selectedPages.add(i)
                        self.selectedGroups[-1].append(i)
            self.selectedPages = sorted(selectedPages)

        print(self.selectedPages)
        print(self.selectedGroups)

    @pyqtSlot()
    def showHelpMsg(self):
        helpMsg = ("Please enter:\n" +
                   "- Average Page: Split every [Input] page.\n" +
                   "  Example: [2].\n" +
                   "- Assigned Pages: Split by page(s) [Input].\n" +
                   "  Example: [3, 7, 11]. (Ends with 3, 7, 11.)\n" +
                   "- Extract Pages: Extract [Input]\n" +
                   "  Example: [1-2, 3, 4-5].")
        msgBox = QMessageBox(1, "Usage", helpMsg,
                             QMessageBox.Ok, self)
        msgBox.setStyleSheet("font: 14px")
        msgBox.exec_()
        # msgBox.question(None, "Usage", helpMsg,
        #                 QMessageBox.Ok, QMessageBox.Ok)
        # QMessageBox.setStyleSheet(self, "font: 14px")
        # QMessageBox.question(self, "Usage", helpMsg,
        #                      QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def onClickSplit(self):
        # TODO: Page Selection Alert
        if len(self.selectedPages) > 0:
            self.splitSignal.emit()
        else:
            msgBox = QMessageBox(1, "Alert", "No pages selected!",
                                 QMessageBox.Ok, self)
            msgBox.setStyleSheet("font: 14px")
            msgBox.exec_()


class FilesMerger(QWidget):
    mergeSignal = pyqtSignal()
    currentFileSetSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.filesDict = {}
        self.currentFile = None
        self.initUI()

    def initUI(self):
        self.buildWidgets()

        layout = QGridLayout()
        layout.addWidget(self.filesListView, 0, 0, 3, 1)
        layout.addWidget(self.noticeLabel, 0, 1, 1, 1)
        layout.addWidget(self.mergeFilesButton, 1, 1, 1, 1)
        # layout.addWidget(self.filesListView, 0, 0, 1, 4)
        # layout.setRowStretch(0, 1)
        layout.setColumnStretch(0, 1)
        # layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def reset(self):
        super().__init__()
        self.filesDict = {}
        self.currentFile = None
        self.initUI()

    def buildWidgets(self):
        # self.filesModel = QStringListModel()
        self.filesModel = QStandardItemModel()

        self.filesListView = QListView()
        self.filesListView.setModel(self.filesModel)
        self.filesListView.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.filesListView.setDragDropOverwriteMode(False)
        self.filesListView.setDragDropMode(QAbstractItemView.InternalMove)
        self.filesListView.setDropIndicatorShown(True)
        self.filesListView.clicked.connect(self.setCurrentFile)

        # TODO: insert introducing image
        # label = QLabel(self)
        # pixmap = QPixmap('cat.jpg')
        # label.setPixmap(pixmap)
        # self.setCentralWidget(label)
        # self.resize(pixmap.width(), pixmap.height())

        self.noticeLabel = QLabel("<< Drag to set file order")

        self.mergeFilesButton = QPushButton("merge")
        self.mergeFilesButton.setAutoDefault(False)
        self.mergeFilesButton.clicked.connect(self.onClickMerge)

    def loadModel(self, fileNames):
        self.filesModel.clear()
        self.filesDict = {fileName[fileName.rfind(
            "/") + 1:]: fileName for fileName in fileNames}
        for file in self.filesDict.keys():
            item = QStandardItem(file)
            item.setFlags(item.flags() ^ Qt.ItemIsDropEnabled)
            self.filesModel.appendRow(item)

    def setCurrentFile(self, index):
        print("Clicked: " + str(index.row()) +
              self.filesModel.data(index, Qt.DisplayRole))
        self.currentFile = self.filesDict[
            self.filesModel.data(index, Qt.DisplayRole)]
        # print("Clicked: " + str(index.row()) +
        #       self.filesModel.stringList()[index.row()])
        # self.currentFile = self.filesDict[
        #     self.filesModel.stringList()[index.row()]]
        self.currentFileSetSignal.emit()

    def getCurrentFile(self):
        return self.currentFile

    def getFilesList(self):
        return [self.filesModel.data(self.filesModel.index(r, 0), Qt.DisplayRole)
                for r in range(self.filesModel.rowCount())]
        # return [self.filesDict[fileName]
        #         for fileName in self.filesModel.stringList()]

    @pyqtSlot()
    def onClickMerge(self):
        self.mergeSignal.emit()


if __name__ == '__main__':
    pass
