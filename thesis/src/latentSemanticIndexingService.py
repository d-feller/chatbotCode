import numpy as np
from scipy import spatial
from sklearn.preprocessing import normalize
from Answer import Answer
from Document import Document
from IRService import IRService
from config import Config
from helperFunctions import getAllUniqueTerms, getTermDocMatrix, getVectorFromQuery

config = Config()


class LSI_IRService(IRService):
    def __init__(self, manualFilepath=config.manualPath, k=60):
        documents = Document(manualFilepath)
        docs = documents.docList
        self.Doc = documents
        self.docTree = documents.tree
        self.nodes = documents.nodeList
        self.uniqueTerms = getAllUniqueTerms(docs)
        self.allTopics = documents.allTopics
        termDocMatrix = getTermDocMatrix(self.uniqueTerms, docs)
        u, s, vh = np.linalg.svd(termDocMatrix, full_matrices=False)
        S = np.diag(s)
        # # ersetzen durch variable K
        self.uk = u[:, :k]
        self.Sk = S[:k, :k]
        self.vhk = vh[:k, :]

    def getTopNAnswers(self, query, n):
        """

        :param query:
        :param n:
        :return:
        """
        answers = []
        cosSimValues = []
        htmlOutput = []
        textOutput = []
        queryVec = getVectorFromQuery(query, self.uniqueTerms)
        lsiQueryVec = np.linalg.inv(self.Sk).dot(np.transpose(self.uk)).dot(queryVec)
        for col in self.vhk.T:
            cosSimValues.append(1. - spatial.distance.cosine(lsiQueryVec, col))

        headlineCosSimValues = self._compareQueryToTopics(query)
        a = np.array(headlineCosSimValues)
        b = np.array(cosSimValues)
        normalizedA = []
        normalizedB = []
        combinedValues = []
        for i in range(len(cosSimValues)):
            normalizedA.append((a[i] - np.min(a)) / (np.max(a) - np.min(a)))
            normalizedB.append((b[i] - np.min(b)) / (np.max(b) - np.min(b)))
        topNhighestScoresIndeces = np.argsort(np.array(cosSimValues))[-n:]
        topNhighestHeadlineScoresIndeces = np.argsort(np.array(headlineCosSimValues))[-n:]
        for i in range(len(topNhighestScoresIndeces)):
            a = topNhighestScoresIndeces[i]
            b = topNhighestHeadlineScoresIndeces[i]
            A = normalizedA[a]
            B = normalizedB[b]
            c = cosSimValues[a]
            d = headlineCosSimValues[b]
            res = a if A > B else b
            topResultNodes = self.nodes[res]
            for node in topResultNodes:
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
            topResultTopicHeadline = topResultNodes[0].topic
            answers.append(Answer(2, textOutput, "".join(htmlOutput), topResultTopicHeadline))
        return answers

    def _compareQueryToTopics(self, query):
        listOfTopicVecs = []
        cosSimValues = []
        queryVec = getVectorFromQuery(query, self.uniqueTerms)
        lsiQueryVec = np.linalg.inv(self.Sk).dot(np.transpose(self.uk)).dot(queryVec)

        for topic in self.allTopics:
            topicVec = getVectorFromQuery(topic, self.uniqueTerms)
            lsiTopicVec = np.linalg.inv(self.Sk).dot(np.transpose(self.uk)).dot(topicVec)
            listOfTopicVecs.append(lsiTopicVec)

        for vec in listOfTopicVecs:
            cosSimValues.append(1. - spatial.distance.cosine(lsiQueryVec, vec))

        return cosSimValues

if __name__ == "__main__":
    lsiService = LSI_IRService('../manuals/html/printer/printerManual.html')
    lsiService._compareQueryToTopics("Thats a joke!")
    print("finished")
