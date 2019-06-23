import os


class config:
    def __init__(self):
        self.manualPath = os.path.abspath('./manuals/html/printer/printerManual.html')
        self.questionAnswerPairsFilepath = os.path.abspath('../questionAnswerPairs.csv')
        self.TERM_DOC_MATRIX_PATH = os.path.abspath("./termDocMatrix.npy")
