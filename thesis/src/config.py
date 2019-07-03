import os


class Config:
    def __init__(self):
        self.manualPath = '../manuals/html/printer/printerManual.html'
        self.questionAnswerPairsFilepath = os.path.abspath('../questionAnswerPairs.csv')
        self.doc2VecModel = './doc2VecModel'
        self.ldaModelFile = './ldaModel'
        self.TERM_DOC_MATRIX_PATH = os.path.abspath("./termDocMatrix.npy")
