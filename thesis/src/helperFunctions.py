import math
import os

import numpy as np

import preprocess as prep
from config import Config

config = Config()


def getAllUniqueTerms(docList):
    uniqueTerms = []
    for doc in docList:
        for term in doc:
            if term not in uniqueTerms:
                uniqueTerms.append(term)
            else:
                continue
    return uniqueTerms


def getTermDocMatrix(termList, docList):
    if os.path.exists(config.TERM_DOC_MATRIX_PATH):
        return np.load(config.TERM_DOC_MATRIX_PATH)
    termDocMatrix = []
    print(len(termList))
    print(len(docList))
    for term in termList:
        row = []
        for doc in docList:
            row.append(calcWeight(term, doc, docList))
        termDocMatrix.append(row)
    np.save(config.TERM_DOC_MATRIX_PATH, termDocMatrix)
    print("calculation of the term-document matrix is finished!")
    return np.array(termDocMatrix)


def getVectorFromQuery(text, uniqueTerms):
    qVector = np.zeros(len(uniqueTerms))
    prepText = prep.preprocessTextInput(text)
    for term in prepText:
        if term in uniqueTerms:
            index = uniqueTerms.index(term)
            qVector[index] = 1
    return qVector


def calcWeight(word, document, allDocuments):
    totalNumOfDocuments = len(allDocuments)
    termFreq = _calcTermFrequency(word, document)
    numOfOcc = _calcNumOfOccurencesInCollection(word, allDocuments)
    if termFreq > 0:
        return (1 + math.log10(totalNumOfDocuments / numOfOcc))
    return 0


def _calcTermFrequency(word, document):
    numOfOccurences = 0
    for token in document:
        if word == token:
            numOfOccurences += 1
    return numOfOccurences


def _calcNumOfOccurencesInCollection(word, allDocs):
    numOfOccurences = 0
    for doc in allDocs:
        if word in doc:
            numOfOccurences += 1
    return numOfOccurences
