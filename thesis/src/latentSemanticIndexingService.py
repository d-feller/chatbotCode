import numpy as np
import scipy

import preprocess as prep
from Answer import Answer
from Document import Document
from IRService import IRService
from config import Config
from helperFunctions import getAllUniqueTerms, getTermDocMatrix, getVectorFromQuery

config = Config()


class LSI_IRService(IRService):
    def __init__(self, manualFilepath=config.manualPath, k=40):
        documents = Document(manualFilepath)
        docs = documents.docList
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
            cosSimValues.append(1. - scipy.spatial.distance.cosine(lsiQueryVec, col))
        topNhighestScoresIndeces = np.argsort(np.array(cosSimValues))[-n:]
        for i in topNhighestScoresIndeces:
            topResultNodes = self.nodes[i]
            for node in topResultNodes:
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
            topResultTopicHeadline = topResultNodes[0].topic
            answers.append(Answer(2, textOutput, "".join(htmlOutput), topResultTopicHeadline))
        return answers


if __name__ == "__main__":
    lsiService = LSI_IRService('./manuals/html/printer/printerManual.html')
    answer = lsiService.getTop10Answers("replace cartridge")
    print(answer)
    print("finished")
