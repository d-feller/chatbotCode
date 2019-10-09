import scipy

from Answer import Answer
from Document import Document
from IRService import IRService
from helperFunctions import *

config = Config()


class CosSim_IRService(IRService):
    def __init__(self, manualFilepath):
        documents = Document(manualFilepath)
        docs = documents.docList
        self.docTree = documents.tree
        self.nodes = documents.nodeList
        self.uniqueTerms = getAllUniqueTerms(docs)
        self.allTopics = documents.allTopics
        self.termDocMatrix = getTermDocMatrix(self.uniqueTerms, docs)

    def getTopNAnswers(self, query, n):
        """
        :param query: The query string
        :param n: The number of the top N answers to retrieve
        :return: List of Answer objects
        """
        answers = []
        cosSimValues = []
        htmlOutput = []
        textOutput = []
        queryVec = getVectorFromQuery(query, self.uniqueTerms)
        for col in self.termDocMatrix.T:
            cosSimValues.append(1. - scipy.spatial.distance.cosine(queryVec, col))
        headlineCosSimValues = self._getTopicSims(query)
        topNhighestScoresIndeces = np.argsort(np.array(cosSimValues))[-n:]
        topNhighestheadlineScoresIndeces = np.argsort(np.array(headlineCosSimValues))[-n:]
        normalizedA = []
        normalizedB = []
        a = cosSimValues
        b = headlineCosSimValues
        for i in range(len(cosSimValues)):
            normalizedA.append((a[i] - np.min(a)) / (np.max(a) - np.min(a)))
            normalizedB.append((b[i] - np.min(b)) / (np.max(b) - np.min(b)))
        for i in range(len(topNhighestScoresIndeces)):
            a = topNhighestScoresIndeces[i]
            b = topNhighestheadlineScoresIndeces[i]
            A = cosSimValues[a]
            B = headlineCosSimValues[b]
            normA = normalizedA[a]
            normB = normalizedB[b]
            res = a if normA > normB else b
            topResultNodes = self.nodes[res]
            for node in topResultNodes:
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
            topResultTopicHeadline = topResultNodes[0].topic
            answers.append(Answer(2, textOutput, "".join(htmlOutput), topResultTopicHeadline))
        return answers

    def _getTopicSims(self, query):
        queryVec = getVectorFromQuery(query, self.uniqueTerms)
        cosSimValues = []
        for topic in self.allTopics:
            topicVec = getVectorFromQuery(topic, self.uniqueTerms)
            cosSimValues.append(1. - scipy.spatial.distance.cosine(queryVec, topicVec))
        return cosSimValues

if __name__ == "__main__":
    service = CosSim_IRService(config.manualPath)
    print(service.getAnswer("The print is black and white"))
