import scipy

from Answer import Answer
from Document import Document
from IRService import IRService
from helperFunctions import *

config = Config()


class CosSimService(IRService):
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
        topNhighestScoresIndeces = np.argsort(np.array(cosSimValues))[-n:]
        for i in topNhighestScoresIndeces:
            topResultNodes = self.nodes[i]
            for node in topResultNodes:
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
            topResultTopicHeadline = topResultNodes[0].topic
            answers.append(Answer(2, textOutput, htmlOutput, topResultTopicHeadline))
        return answers


if __name__ == "__main__":
    service = CosSimService(config.manualPath)
    print(service.getAnswer("The print is black and white"))
