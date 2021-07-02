import os
import shutil


def runGs(gsPath, inFile, outFile):
    settings = "-q -dNOPAUSE -dBATCH -dSAFER -dPDFA=2 \
                -dPDFACompatibilityPolicy=1 -dOverprint=/enable \
                -sDEVICE=pdfwrite -dCompatibilityLevel=1.3 \
                -dPDFSETTINGS=/screen -dEmbedAllFonts=true \
                -dSubsetFonts=true -dAutoRotatePages=/None \
                -dColorImageDownsampleType=/Bicubic \
                -dColorImageResolution=150 \
                -dGrayImageDownsampleType=/Bicubic \
                -dGrayImageResolution=150 \
                -dMonoImageDownsampleType=/Bicubic \
                -dMonoImageResolution=150 -sOutputFile="
    if inFile == outFile:
        os.system("{} {}{} {}".format(gsPath, settings, "gs.pdf", inFile))
        shutil.move("gs.pdf", outFile)

    os.system("{} {}{} {}".format(gsPath, settings, inFile, outFile))
