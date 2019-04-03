from anytree.iterators import PreOrderIter
import preprocess as prep
import scipy
import math
import numpy as np
import json
import collections
import os
from parseHTMLtoTree import getTree


def getDocumentsList():
    docList = []
    filepath = './manuals/html/printer/printerManual.html'
    tree = getTree(filepath)
    for topic in tree.children:
        if len(topic.children) == 1:
            textList = " ".join(
                [node.data.getText() for node in PreOrderIter(topic)])
            docList.append(prep.preprocessTextInput(textList))
        if len(topic.children) > 1:
            for subtopic in topic.children:
                textList = " ".join(
                    [node.data.getText() for node in PreOrderIter(subtopic)])
                docList.append(prep.preprocessTextInput(textList))
    return docList


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
    termDocMatrix = []
    for term in termList:
        row = []
        for doc in docList:
            row.append(calcWeight(term, doc, docList))
        termDocMatrix.append(row)
    print(termDocMatrix)


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


if __name__ == "__main__":
    docs = getDocumentsList()
    terms = getAllUniqueTerms(docs)
    getTermDocMatrix(terms, docs)
# termDocumentMatrix = np.matrix(termDocArray)
# termDocumentMatrix = termDocumentMatrix.T
# u, s, vh = np.linalg.svd(termDocumentMatrix, full_matrices=False)
# S = np.diag(s)
# print(S)
# print(u.shape, S.shape, vh.shape)
# # ersetzen durch variable K
# uk = u[:, :10]
# Sk = S[:10, :10]
# vhk = vh[:10, :]
#
# queryVector = getVectorFromQuery("Set up a Bluetooth wireless connection ")
# qVector = np.array(queryVector)
# newQueryVector = np.dot(np.dot(qVector.T,uk), np.linalg.inv(Sk))
#
# result = []
# for vec in vhk.T:
#   result.append(1. - scipy.spatial.distance.cosine(newQueryVector, vec))
#
# result = np.array(result)
# print(result)
# print( np.argmax(result), result[np.argmax(result)])
# print(filesList[np.argmax(result)])
