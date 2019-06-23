import scipy
from anytree.iterators import PreOrderIter

from Answer import Answer
from Document import Document
from config import config
from helperFunctions import *


class LSI_Service():
    def __init__(self, manualFilepath):
        documents = Document(manualFilepath)
        docs = documents.docList
        self.docTree = documents.tree
        self.nodes = documents.nodeList
        self.terms = getAllUniqueTerms(docs)
        self.allTopics = documents.allTopics
        termDocMatrix = getTermDocMatrix(self.terms, docs)
        u, s, vh = np.linalg.svd(termDocMatrix, full_matrices=False)
        S = np.diag(s)
        # # ersetzen durch variable K
        self.uk = u[:, :100]
        self.Sk = S[:100, :100]
        self.vhk = vh[:100, :]

    def compareToTopics(self, query):
        """
        This functions takes a query and returns the most probable topic
        and score.
        :param query: string
        :return:  topic, score
        """
        allTerms = []
        # what the fuck are you doing, this is bullshit! xD
        
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

    def getAnswer(self, query):
        """
        :param query: string
        :return: string
        """
        textOutput = []
        htmlOutput = []
        result = []
        probableTopic, topicScore = self.compareToTopics(query)
        if topicScore >= 0.9:
            topicNodes = list(node for node in PreOrderIter(self.docTree, filter_=lambda n: n.topic == probableTopic))
            print("Thats probably the topic: ", probableTopic)
            for node in topicNodes:
                print(node)
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
        else:
            queryVector = getVectorFromQuery(query, self.terms)
            newQueryVector = np.dot(np.dot(queryVector.T, self.uk), np.linalg.inv(self.Sk))
            for vec in self.vhk.T:
                result.append(1. - scipy.spatial.distance.cosine(newQueryVector, vec))
            resArr = np.array(result)
            indeces = resArr.argsort()[-3:]
            top3ResultsValues = resArr[indeces]
            if top3ResultsValues[-1:] <= 0.5:
                top3topics = []
                for index in indeces:
                    top3topics.append(self.nodes[index][0].topic)
                htmlOutput.append("I am not sure what you mean. Can you rephrase your question?" \
                                  "Is it one of these topics? " \
                       "<br><br>" \
                                  + top3topics[0] + \
                       "<br><br>" \
                                  + top3topics[1] + \
                       "<br><br>" \
                                  + top3topics[2])
            for node in self.nodes[np.argmax(result)]:
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
        return Answer(2, textOutput, htmlOutput, probableTopic)


if __name__ == "__main__":
    config = config()
    lsiService = LSI_Service(config.manualPath)
    print(lsiService.vhk.shape)
    print("hi")
