from anytree.iterators import PreOrderIter
import preprocess as prep
import re
import scipy
import math
import numpy as np
import json
import collections
import os
from parseHTMLtoTree import getTree

TERM_DOC_MATRIX_PATH = os.path.abspath("./termDocMatrix.npy")
MANUAL_PATH = os.path.abspath('./manuals/html/printer/printerManual.html')

class Document():
    def __init__(self):
        self.docList = []
        self.nodeList = []
        filepath = MANUAL_PATH 
        self.tree, allTopics = getTree(filepath)
        self.allTopics = list(allTopics)
        for topic in self.tree.children:
            if len(topic.children) == 1:
                chain = [node.data.getText(" ") for node in PreOrderIter(topic)]
                textList = " ".join(chain)
                self.docList.append(prep.preprocessTextInput(textList))
                self.nodeList.append([node for node in PreOrderIter(topic)])
            if len(topic.children) > 1:
                for subtopic in topic.children:
                    chain = [node.data.getText(" ") for node in PreOrderIter(subtopic)]
                    textList = " ".join(chain)
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
        self.docTree = documents.tree
        self.nodes = documents.nodeList
        self.terms = getAllUniqueTerms(docs)
        self.allTopics = documents.allTopics
        termDocMatrix = getTermDocMatrix(self.terms, docs)
        u, s, vh = np.linalg.svd(termDocMatrix, full_matrices=False)
        S = np.diag(s)
    # # ersetzen durch variable K
        self.uk = u[:, :50]
        self.Sk = S[:50, :50]
        self.vhk = vh[:50, :]

    def compareToTopics(self, query):
        """
        This functions takes a query and returns the most probable topic
        and score.
        :param query: string
        :return:  topic, score
        """
        allTerms = []
        for topic in self.allTopics:
            for word in topic.split(" "):
                newText = prep.removeSpecialCharactersAndToLower(word)
                if newText not in allTerms:
                    allTerms.append(newText)
        for word in query.split(" "):
            newText = prep.removeSpecialCharactersAndToLower(word)
            if newText not in allTerms:
                allTerms.append(newText)

        numOfTerms = len(allTerms)
        queryVector = np.zeros(numOfTerms)
        for word in query.split(" "):
            index = allTerms.index(prep.removeSpecialCharactersAndToLower(word))
            queryVector[index] += 1
        simValues = []
        for topic in self.allTopics:
            topicVector = np.zeros(numOfTerms)
            for word in topic.split(" "):
                index = allTerms.index(prep.removeSpecialCharactersAndToLower(word))
                topicVector[index] += 1
            simValues.append(1. - scipy.spatial.distance.cosine(queryVector, topicVector))
        resultArr = np.array(simValues)
        return self.allTopics[resultArr.argmax()], np.amax(resultArr)

    def getAnswer(self, query, format="HTML"):
        output = []
        topicNodes = []
        result = []
        probaleTopic, topicScore = self.compareToTopics(query)
        if topicScore >= 0.9:
            topicNodes = list(node for node in PreOrderIter(self.docTree, filter_=lambda n: n.topic == probaleTopic))
            print("Thats probably the topic: ", probaleTopic)
            for node in topicNodes:
                print(node)
                if format == "HTML":
                    output.append(str(node.data))
                elif format == "TEXT":
                    output.append(node.data.getText())
        else:
            queryVector = getVectorFromQuery(query, self.terms)
            newQueryVector = np.dot(np.dot(queryVector.T, self.uk), np.linalg.inv(self.Sk))
            for vec in self.vhk.T:
              result.append(1. - scipy.spatial.distance.cosine(newQueryVector, vec))
            resArr = np.array(result)
            indeces = resArr.argsort()[-3:]
            top3ResultsValues = resArr[indeces]
            print('Top 3 Results Values: ', top3ResultsValues)
            if top3ResultsValues[-1:] <= 0.5:
                top3topics = []
                for index in indeces:
                    top3topics.append(self.nodes[index][0].topic)
                return "I am not sure what you mean. Can you rephrase your question?" \
                       "Is it one of these topics? " \
                       "<br><br>" \
                       + top3topics[0] + \
                       "<br><br>" \
                       + top3topics[1] + \
                       "<br><br>" \
                       + top3topics[2]
            for node in self.nodes[np.argmax(result)]:
                if format == "HTML":
                    output.append(str(node.data))
                elif format == "TEXT":
                    output.append(node.data.getText())
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
    #----------------------------------------------------------
    service = LSI_Service()
    print(service.compareToTopics("bottom view"))

