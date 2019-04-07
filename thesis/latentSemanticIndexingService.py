from anytree.iterators import PreOrderIter
import preprocess as prep
import scipy
import math
import numpy as np
import json
import collections
import os
from parseHTMLtoTree import getTree

TERM_DOC_MATRIX_PATH = os.path.abspath("./termDocMatrix.npy")
MANUAL_PATH = os.path.abspath('./manuals/html/printer/printerManual.html')

class Document:
    def __init__(self):
        self.docList = []
        self.nodeList = []
        filepath = MANUAL_PATH 
        tree = getTree(filepath)
        for topic in tree.children:
            if len(topic.children) == 1:
                textList = " ".join(
                    [node.data.getText() for node in PreOrderIter(topic)])
                self.docList.append(prep.preprocessTextInput(textList))
                self.nodeList.append([node for node in PreOrderIter(topic)])
            if len(topic.children) > 1:
                for subtopic in topic.children:
                    textList = " ".join(
                        [node.data.getText() for node in PreOrderIter(subtopic)])
                    self.docList.append(prep.preprocessTextInput(textList))
                    self.nodeList.append([node for node in PreOrderIter(subtopic)])


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
    if os.path.exists(TERM_DOC_MATRIX_PATH):
        return np.load(TERM_DOC_MATRIX_PATH)
    termDocMatrix = []
    for term in termList:
        row = []
        for doc in docList:
            row.append(calcWeight(term, doc, docList))
        termDocMatrix.append(row)
    np.save(TERM_DOC_MATRIX_PATH, termDocMatrix)
    print("calculation of the term-document matrix is finished!")
    return np.array(termDocMatrix)

def getVectorFromQuery (text, uniqueTerms):
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

class LSI_Service():
    def __init__(self, k=10):
        documents = Document()
        docs = documents.docList
        self.nodes = documents.nodeList
        self.terms = getAllUniqueTerms(docs)
        termDocMatrix = getTermDocMatrix(self.terms, docs)
        u, s, vh = np.linalg.svd(termDocMatrix, full_matrices=False)
        S = np.diag(s)
    # # ersetzen durch variable K
        self.uk = u[:, :100]
        self.Sk = S[:100, :100]
        self.vhk = vh[:100, :]

    def getAnswer(self, query):
        queryVector = getVectorFromQuery(query, self.terms)
        newQueryVector = np.dot(np.dot(queryVector.T,self.uk), np.linalg.inv(self.Sk))
        result = []
        output = []
        for vec in self.vhk.T:
          result.append(1. - scipy.spatial.distance.cosine(newQueryVector, vec))
        for node in self.nodes[np.argmax(result)]:
            output.append(str(node.data))
        return " ".join(output)

if __name__ == "__main__":
    documents = Document()
    docs = documents.docList
    nodes = documents.nodeList
    terms = getAllUniqueTerms(docs)
    termDocMatrix = getTermDocMatrix(terms, docs)
    u, s, vh = np.linalg.svd(termDocMatrix, full_matrices=False)
    S = np.diag(s)
# # ersetzen durch variable K
    uk = u[:, :10]
    Sk = S[:10, :10]
    vhk = vh[:10, :]

    queryVector = getVectorFromQuery("Where is the off button", terms)
    newQueryVector = np.dot(np.dot(queryVector.T,uk), np.linalg.inv(Sk))
    result = []
    for vec in vhk.T:
      result.append(1. - scipy.spatial.distance.cosine(newQueryVector, vec))
    for node in nodes[np.argmax(result)]:
        print(node.data.getText())
