import PyPDF3
import shutil
import os
from datetime import datetime
from third_party.gsRunner import runGs


class FileBase():
    def __init__(self, config):
        self.initFiles(config)

    def initFiles(self, config=None):
        self.rootPath = os.getcwd() + "\\"
        self.selectedFiles = []
        self.originalTempFiles = []
        self.currentTempFiles = []
        self.displayedFiles = None
        self.container = {}
        if config:
            self.outPath = config["default"]["saveFilePath"]
            self.tmpPath = config["default"]["tmpFilePath"]
            self.previewFileName = config["default"]["tmpPreviewFileName"]
            self.tmpPreviewFile = "{}{}".format(self.tmpPath,
                                                self.previewFileName)
            self.timeStampStyle = config["backend"]["timeStampStyle"].strip(
                "'")
            self.gsPath = config["backend"]["gsPath"]
            print(self.rootPath)
        self.makeDir(self.outPath)
        self.makeDir(self.tmpPath, self.clearTempFiles)
        # if not os.path.exists(self.outPath):
        #     os.mkdir(self.outPath)
        # if not os.path.exists(self.tmpPath):
        #     os.mkdir(self.tmpPath)
        # else:
        #     self.clearTempFiles()

    def makeDir(self, dirName, alt=None):
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        elif alt:
            alt()

    def clearTempFiles(self):
        header, _, fileNames = list(os.walk(self.tmpPath))[0]
        for f in fileNames:
            os.remove("{}\\{}".format(header, f))

    def load(self, paths):
        self.initFiles()
        self.selectedFiles = paths
        self.originalTempFiles = ["{}{}.easyOrigin_{}".format(
            self.rootPath, self.tmpPath, os.path.split(p)[1])
            for p in paths]
        self.currentTempFiles = ["{}{}.easyCurrent_{}".format(
            self.rootPath, self.tmpPath, os.path.split(p)[1])
            for p in paths]
        self.save(paths, self.originalTempFiles)
        self.save(paths, self.currentTempFiles)
        for path in self.currentTempFiles:
            self.container[path] = path

    def save(self, src, dst=None):
        if dst:
            assert (len(src) == len(dst))

            for s, d in zip(src, dst):
                shutil.copyfile(s, d)
        else:
            assert (len(src) == len(self.currentTempFiles))

            for s, d in zip(self.currentTempFiles, src):
                shutil.copyfile(s, d)

    def getOutDir(self):
        return self.outPath


class MainEngine(FileBase):
    def __init__(self, config):
        super().__init__(config)
        self.initModules()

    def __del__(self):
        self.clearTempFiles()

    def initModules(self):
        self.currentFileName = None
        self.readers = {}
        self.origins = {}

    def loadFiles(self, paths):
        self.load(paths)
        self.setCurrentFile(self.currentTempFiles[0])
        for fileName in self.currentTempFiles:
            self.readers[fileName] = PyPDF3.PdfFileReader(fileName)
            self.origins[fileName] = (PyPDF3.PdfFileReader(fileName),
                                      self.container[fileName])

    def saveFiles(self, pages, path=None):
        resultFile = PyPDF3.PdfFileWriter()
        for page in pages:
            resultFile.addPage(page)
        if path:
            with open(path, "wb") as resultFileStream:
                resultFile.write(resultFileStream)
            runGs(self.gsPath, path, path)
        else:
            with open(self.tmpPreviewFile, "wb") as resultFileStream:
                resultFile.write(resultFileStream)

            self.readers[self.currentFileName] = PyPDF3.PdfFileReader(
                self.tmpPreviewFile)

            self.container[self.currentFileName] = self.tmpPreviewFile

    def saveCurrentFile(self, path):
        if not path.endswith(".pdf"):
            path += ".pdf"
        if os.path.exists(self.tmpPreviewFile):
            shutil.copyfile(self.tmpPreviewFile, path)
            runGs(self.gsPath, path, path)

    def mergeFiles(self, paths, savePath):
        merger = PyPDF3.PdfFileMerger()
        for path in paths:
            merger.append(path)
        merger.write(savePath)
        runGs(self.gsPath, savePath, savePath)

    def createBlankPage(self, width, height):
        return PyPDF3.pdf.PageObject.createBlankPage(None, width, height)

    def getDisplayedFile(self):
        # return self.currentFileName
        print(self.container.keys())
        return self.container[self.currentFileName]

    def setCurrentFile(self, fileName):
        if ".easyCurrent_" in fileName:
            self.currentFileName = fileName
        else:
            _, tail = os.path.split(fileName)
            self.currentFileName = "{}{}.easyCurrent_{}".format(
                self.rootPath, self.tmpPath, tail)

    def getOriginalFile(self) -> PyPDF3.PdfFileReader:
        if self.currentFileName:
            print(self.currentFileName, self.origins.keys())
            return self.origins[self.currentFileName][0]

    def getCurrentFile(self) -> PyPDF3.PdfFileReader:
        if self.currentFileName:
            return self.readers[self.currentFileName]

    def getTimeStamp(self):
        now = datetime.now()
        return now.strftime(self.timeStampStyle)
        # return now.strftime(r"%Y%m%d%H%M%S")

    def resetFiles(self):
        if len(self.currentTempFiles) > 0:
            self.save(self.originalTempFiles,
                      self.currentTempFiles)
            self.readers[self.currentFileName] = self.getOriginalFile()
            self.container[self.currentFileName] = self.origins[self.currentFileName][1]
            return True

        return False
