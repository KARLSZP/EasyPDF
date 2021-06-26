from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from .backend import MainEngine
from .widgets import *
import sys


class EasyPDF_GUI(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.initConfig(config)
        self.initUI()
        self.engine = MainEngine(config)

    def initConfig(self, config):
        self.setWindowTitle(
            "EasyPDF - v{}".format(config["default"]["version"]))
        self.setStyle(QStyleFactory.create(config["gui"]["windowStyle"]))
        self.setGeometry(*[int(x) for x in config["gui"]
                           ["windowGeometry"].strip().split(',')])
        self.saveDir = config["default"]["saveFilePath"]
        self.tmpDir = config["default"]["tmpFilePath"]
        self.saveName = config["default"]["saveFileName"]
        self.saveNameNoPage = config["default"]["saveFileName"]

    def initUI(self):
        self.createViewer()
        self.createFileSelectionGroupBox()
        self.createMergeFunction()
        self.createScaleFunction()
        self.createFilesMergeFunction()
        self.createSplitFunction()
        self.createFunctionTabs()
        self.createFileWiseGroupBox()
        self.createFilesWiseGroupBox()
        self.createAboutGroupBox()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.fileSelectionGroupBox, 0, 0, 1, 1)
        mainLayout.addWidget(self.fileWiseGroupBox, 1, 0, 1, 1)
        mainLayout.addWidget(self.filesWiseGroupBox, 2, 0, 1, 1)
        mainLayout.addWidget(self.aboutGroupBox, 3, 0, 1, 1)
        # mainLayout.addWidget(self.viewerGroupBox, 0, 1, 3, 2)
        mainLayout.addWidget(self.viewer, 0, 1, 4, 2)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 2)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 2)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def createFunctionTabs(self):
        # one-file-wise
        self.fileFunctionTabs = QTabWidget()
        fileFunction = {
            "MergePages": self.merger,
            "ScalePages": self.scaler,
            "SplitPages": self.splitter,
        }

        for k, v in fileFunction.items():
            self.fileFunctionTabs.addTab(v, k)

        # multi-files-wise
        self.filesFunctionTabs = QTabWidget()
        filesFunction = {
            "MergeFiles": self.fileMerger,
        }

        for k, v in filesFunction.items():
            self.filesFunctionTabs.addTab(v, k)

    # Widgets initialization
    def createViewer(self):
        self.viewer = Viewer()

    def createFileSelectionGroupBox(self):
        self.fileSelectionGroupBox = QGroupBox("File Controller")
        layout = QVBoxLayout()
        self.fileSelector = FileSelector()
        self.fileSelector.fileSelectedSignal.connect(self.onClickFilesSelect)
        self.fileSelector.currentFileSetSignal.connect(self.setCurrentFile)
        self.fileSelector.fileSavedSignal.connect(self.onClickFileSave)

        layout.addWidget(self.fileSelector)
        self.fileSelectionGroupBox.setLayout(layout)

    def createMergeFunction(self):
        self.merger = PageMerger()
        self.merger.mergeSignal.connect(self.mergePages)
        self.merger.resetSignal.connect(self.onClickResetFiles)

    def createScaleFunction(self):
        self.scaler = PageScaler()
        self.scaler.scaleSignal.connect(self.scalePages)
        self.scaler.resetSignal.connect(self.onClickResetFiles)

    def createFilesMergeFunction(self):
        self.fileMerger = FilesMerger()
        self.fileMerger.mergeSignal.connect(self.mergeFiles)
        self.fileMerger.currentFileSetSignal.connect(self.toggleCurrentFile)

    def createSplitFunction(self):
        self.splitter = PageSplitter()
        self.splitter.splitSignal.connect(self.splitFile)

    def createFileWiseGroupBox(self):
        self.fileWiseGroupBox = QGroupBox("1-File-wise")
        fileWiseGroupBoxLayout = QGridLayout()
        fileWiseGroupBoxLayout.addWidget(self.fileFunctionTabs)
        fileWiseGroupBoxLayout.setRowStretch(0, 1)
        self.fileWiseGroupBox.setLayout(fileWiseGroupBoxLayout)

    def createFilesWiseGroupBox(self):
        self.filesWiseGroupBox = QGroupBox("Multi-Files-wise")
        filesWiseGroupBoxLayout = QGridLayout()
        filesWiseGroupBoxLayout.addWidget(self.filesFunctionTabs)
        filesWiseGroupBoxLayout.setRowStretch(0, 1)
        self.filesWiseGroupBox.setLayout(filesWiseGroupBoxLayout)

    def createAboutGroupBox(self):
        self.aboutGroupBox = QGroupBox("About")
        aboutGroupBoxLayout = QGridLayout()
        aboutTexts = ["Welcome to EasyPDF - @KarlSzp",
                      "Email: <a href='mailto: songzhp3@gmail.com'>songzhp3@gmail.com</a>",
                      "Github: <a href='https://github.com/KARLSZP'>@KARLSZP</a>",
                      "Issue: <a href='https://github.com/KARLSZP/EasyPDF/issues'>@EasyPDF</a>"]
        for aboutText in aboutTexts:
            aboutLabel = QLabel(aboutText)
            aboutLabel.setOpenExternalLinks(True)
            aboutLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
            aboutLabel.setTextFormat(Qt.RichText)
            aboutLabel.setAlignment(Qt.AlignCenter)
            aboutLabel.adjustSize()
            # aboutLabel.setStyleSheet("border: 1px solid black;")
            aboutGroupBoxLayout.addWidget(aboutLabel)

        self.aboutGroupBox.setLayout(aboutGroupBoxLayout)

    def buildPath(self, pattern, op=None, ts=None, sp=None, ep=None):
        pathDict = {
            '[op]': op,
            '[ts]': ts,
            '[sp]': sp,
            '[ep]': ep}

        dirName = self.saveDir + ts + "/"
        self.engine.makeDir(dirName)

        outName = pattern
        for k, v in pathDict.items():
            if k:
                outName = outName.replace(
                    k, v if isinstance(v, str) else str(v))

        return dirName + outName

    # Functions
    def mergePages(self):
        mergePages, margin = self.merger.getMergeConfig()
        currentFile = self.engine.getOriginalFile()
        originPages = currentFile.getNumPages()
        page0 = currentFile.getPage(0)
        originWidth = float(page0.mediaBox.getWidth())
        originHeight = float(page0.mediaBox.getHeight())

        resultPages = originPages // mergePages + \
            (1 if originPages % mergePages else 0)

        # resultFile = PyPDF3.PdfFileWriter()
        newPages = []

        if mergePages == 2:
            if originHeight > originWidth:
                newWidth = (originHeight - 3 * margin) / 2
                newHeight = originWidth - 2 * margin
                scale = min(newWidth / originWidth,
                            newHeight / originHeight)
                newWidth = originWidth * scale
                newHeight = originHeight * scale
                marginX = (originWidth - newHeight) / 2
                marginY = (originHeight - 2 * newWidth) / 3
                for i in range(resultPages):
                    newPage = self.engine.createBlankPage(
                        originWidth, originHeight)
                    if i * mergePages > originPages - 1:
                        break
                    newPage.mergeRotatedScaledTranslatedPage(
                        currentFile.getPage(i * mergePages),
                        90, scale, marginX + newHeight, marginY)
                    if i * mergePages + 1 > originPages - 1:
                        break
                    newPage.mergeRotatedScaledTranslatedPage(
                        currentFile.getPage(i * mergePages + 1),
                        90, scale, marginX + newHeight, 2 * marginY + newWidth)
                    newPages.append(newPage)
            else:
                newWidth = originHeight - 2 * margin
                newHeight = (originWidth - 3 * margin) / 3
                scale = min(newWidth / originWidth,
                            newHeight / originHeight)
                newWidth = originWidth * scale
                newHeight = originHeight * scale
                marginX = (originWidth - 2 * newHeight) / 3
                marginY = (originHeight - newWidth) / 2
                for i in range(resultPages):
                    newPage = self.engine.createBlankPage(
                        originWidth, originHeight)
                    if i * mergePages > originPages - 1:
                        break
                    newPage.mergeRotatedScaledTranslatedPage(
                        currentFile.getPage(i * mergePages),
                        90, scale, marginX + newHeight, marginY)
                    if i * mergePages + 1 > originPages - 1:
                        break
                    newPage.mergeRotatedScaledTranslatedPage(
                        currentFile.getPage(i * mergePages + 1),
                        90, scale, 2 * (marginX + newHeight), marginY)
                    newPages.append(newPage)

        else:
            newWidth = (originWidth - 3 * margin) / 2
            newHeight = (originHeight -
                         (mergePages // 2 + 1) * margin) / (mergePages // 2)
            scale = min(newWidth / originWidth,
                        newHeight / originHeight)
            newWidth = originWidth * scale
            newHeight = originHeight * scale
            marginX = (originWidth - 2 * newWidth) / 3
            marginY = (originHeight - (mergePages // 2) *
                       newHeight) / (mergePages // 2 + 1)
            ty = [originHeight - (i + 1) *
                  (marginY + newHeight) for i in range(mergePages // 2)]
            for i in range(resultPages):
                newPage = self.engine.createBlankPage(
                    originWidth, originHeight)
                for j in range(0, mergePages, 2):
                    if j + i * mergePages > originPages - 1:
                        break
                    newPage.mergeScaledTranslatedPage(
                        currentFile.getPage(j + i * mergePages),
                        scale, originWidth / 2 - newWidth - marginX / 2, ty[j // 2])
                    if j + 1 + i * mergePages > originPages - 1:
                        break
                    newPage.mergeScaledTranslatedPage(
                        currentFile.getPage(j + 1 + i * mergePages),
                        scale, (originWidth + marginX) // 2, ty[j // 2])
                newPages.append(newPage)

        self.engine.saveFiles(newPages)
        bytesPDF = self.engine.getDisplayedFile()
        numPages = self.engine.getCurrentFile().getNumPages()
        self.viewer.loadFile(bytesPDF, numPages)

    def scalePages(self):
        currentFile = self.engine.getOriginalFile()
        pages = [currentFile.getPage(i-1)
                 for i in self.scaler.getSelectedPages()
                 if i <= currentFile.getNumPages()]

        scaleRate = self.scaler.getScaleRate()

        newPages = []

        for i in pages:
            # Zoom out: outW/H = scaleRate * originW/H
            width = i.mediaBox.getWidth()
            height = i.mediaBox.getHeight()
            i.scaleBy(scaleRate)
            if scaleRate > 1.0:
                biasX = (i.mediaBox.getWidth() - width) / 2
                biasY = (i.mediaBox.getHeight() - height) / 2
                i.trimBox.lowerLeft = (biasX, biasY)
                i.trimBox.upperRight = (biasX + width, biasY + height)
                i.cropBox.lowerLeft = (biasX, biasY)
                i.cropBox.upperRight = (biasX + width, biasY + height)
            else:
                paddingX = (width - i.mediaBox.getWidth()) / 2
                paddingY = (height - i.mediaBox.getHeight()) / 2
                newPage = self.engine.createBlankPage(width, height)
                newPage.mergeTranslatedPage(i, paddingX, paddingY)
                i = newPage
            newPages.append(i)

        # with open(destName, "wb") as resultFileStream:
        #     resultFile.write(resultFileStream)
        # self.pageReader = PyPDF3.PdfFileReader(self.originName)
        self.engine.saveFiles(newPages)
        bytesPDF = self.engine.getDisplayedFile()
        numPages = self.engine.getCurrentFile().getNumPages()
        self.viewer.loadFile(bytesPDF, numPages)

    def mergeFiles(self):
        savePath = self.buildPath(
            self.saveNameNoPage, "merged", self.engine.getTimeStamp())
        self.engine.mergeFiles(self.fileMerger.getFilesList(), savePath)

    def splitFile(self):
        mode = self.splitter.getStrategy()
        currentFile = self.engine.getCurrentFile()
        timeStamp = self.engine.getTimeStamp()

        if mode == self.splitter.AverageMode:
            step = self.splitter.getSelectedPages()[0]
            groups = [[(i + j) for j in range(step)
                       if i + j < currentFile.getNumPages()]
                      for i in range(0, currentFile.getNumPages(), step)]
            pages = [[currentFile.getPage(i + j) for j in range(step)
                      if i + j < currentFile.getNumPages()]
                     for i in range(0, currentFile.getNumPages(), step)]
            for idx, page in enumerate(pages):
                savePath = self.buildPath(
                    self.saveName, "splitted", timeStamp, groups[idx][0] + 1, groups[idx][-1] + 1)
                self.engine.saveFiles(page, savePath)

        elif mode == self.splitter.AssignedMode:
            anchors = self.splitter.getSelectedPages()
            anchors = [anchor - 1 for anchor in anchors]
            idx = 0
            startPage = 0
            pages = []
            for i in range(currentFile.getNumPages()):
                if idx >= len(anchors) or i <= anchors[idx]:
                    pages.append(currentFile.getPage(i))
                else:
                    savePath = self.buildPath(
                        self.saveName, "splitted", timeStamp, startPage + 1, anchors[idx] + 1)
                    self.engine.saveFiles(pages, savePath)
                    startPage = anchors[idx] + 1
                    pages = [currentFile.getPage(i)]
                    idx += 1
            if len(pages) > 0:
                savePath = self.buildPath(
                    self.saveName, "splitted", timeStamp, startPage + 1, currentFile.getNumPages())
                self.engine.saveFiles(pages, savePath)

        elif mode == self.splitter.ExtractingMode:
            groups = self.splitter.getSelectedGroups()
            pages = [[currentFile.getPage(page - 1) for page in group]
                     for group in groups]
            for idx, page in enumerate(pages):
                savePath = self.buildPath(
                    self.saveName, "extracted", timeStamp, groups[idx][0], groups[idx][-1])
                self.engine.saveFiles(page, savePath)

    # Slots
    @pyqtSlot()
    def setCurrentFile(self):
        self.engine.setCurrentFile(self.fileSelector.getCurrentFile())
        bytesPDF = self.engine.getDisplayedFile()
        numPages = self.engine.getCurrentFile().getNumPages()
        self.viewer.loadFile(bytesPDF, numPages)
        self.scaler.setPagesSelection("1-{}".format(numPages))

    @pyqtSlot()
    def onClickFilesSelect(self):
        fileNames = self.fileSelector.getFileNames()
        if fileNames:
            self.engine.loadFiles(fileNames)
            bytesPDF = self.engine.getDisplayedFile()
            numPages = self.engine.getCurrentFile().getNumPages()
            self.viewer.loadFile(bytesPDF, numPages)
            self.scaler.setPagesSelection("1-{}".format(numPages))
            self.fileMerger.loadModel(fileNames)
            # self.filesWiseGroupBox.setDisabled((len(fileNames) <= 1))
            # self.fileWiseGroupBox.setDisabled((len(fileNames) > 1))

    @pyqtSlot()
    def onClickFileSave(self):
        fileName = self.fileSelector.getSaveFileName()
        if fileName:
            self.engine.saveCurrentFile(fileName)

    @pyqtSlot()
    def onClickResetFiles(self):
        if self.engine.resetFiles():
            bytesPDF = self.engine.getDisplayedFile()
            numPages = self.engine.getCurrentFile().getNumPages()
            self.viewer.loadFile(bytesPDF, numPages)

    @pyqtSlot()
    def toggleCurrentFile(self):
        currentFile = self.fileMerger.getCurrentFile()
        self.engine.setCurrentFile(currentFile)
        self.fileSelector.currentFileComboBox.setCurrentText(currentFile)
        bytesPDF = self.engine.getDisplayedFile()
        numPages = self.engine.getCurrentFile().getNumPages()
        self.viewer.loadFile(bytesPDF, numPages)
        self.scaler.setPagesSelection("1-{}".format(numPages))


def run():
    app = QApplication(sys.argv)
    easyPDF = EasyPDF_GUI()
    easyPDF.show()
    app.exec_()


if __name__ == '__main__':

    sys.exit(run())
