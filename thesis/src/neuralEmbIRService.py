import numpy as np
from gensim.models import Word2Vec

from Answer import Answer
from Document import Document
from IRService import IRService
from config import Config
from preprocess import preprocessTextInput as prepInput
from pathlib import Path

c = Config()


class neuralEmb_IRService(IRService):
    def __init__(self):
        super()
        self.document = Document()
        self.nodes = self.document.nodeList
        self.docs = [item.lower().split() for item in self.document.rawDocList]
        if Path('word2vecTrained.model').exists():
            self.word2Vec = Word2Vec.load('word2vecTrained.model')
        else:
            self.word2Vec = Word2Vec(self.docs, size=100, window=4, min_count=1, workers=3)
            self.word2Vec.save('word2vecTrained.model')
        #self.model = KeyedVectors.load_word2vec_format(c.trainedWordVectors)

    def getTopNAnswers(self, query, n):
        # prepQuery = query.lower().split()
        prepQuery = prepInput(query)
        distances = []
        answers = []
        htmlOutput = []
        textOutput = []
        for doc in self.docs:
            # distances.append(self.model.wmdistance(prepQuery, doc))
            distances.append(self.word2Vec.wv.wmdistance(prepQuery, doc))
        npDistances = np.array(distances)
        npHeadlineDistances = self._compareToTopics(query)
        a = npDistances
        b = npHeadlineDistances
        normalizedA = []
        normalizedB = []
        for i in range(len(a)):
            normalizedA.append((a[i] - np.min(a)) / (np.max(a) - np.min(a)))
            normalizedB.append((b[i] - np.min(b)) / (np.max(b) - np.min(b)))
        resultsIndeces = np.argsort(npDistances)[:n]
        resultsHeadlineIndeces = np.argsort(npHeadlineDistances)[:n]
        for i in range(len(resultsIndeces)):
            a = resultsIndeces[i]
            b = resultsHeadlineIndeces[i]
            A = normalizedA[a]
            B = normalizedB[b]
            res = a if A < B else b
            topResultNodes = self.nodes[res]
            for node in topResultNodes:
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
            topResultTopicHeadline = topResultNodes[0].topic
            answers.append(Answer(2, textOutput, "".join(htmlOutput), topResultTopicHeadline))
        return answers

    def _compareToTopics(self, query):
        prepQuery = prepInput(query)
        distances = []
        for topic in self.document.allTopics:
            prepTopic = prepInput(topic)
            # distances.append(self.model.wmdistance(prepQuery, doc))
            distances.append(self.word2Vec.wv.wmdistance(prepQuery, prepTopic))
        npDistances = np.array(distances)
        return npDistances
if __name__ == "__main__":
    s = neuralEmb_IRService()
    print(s.getTopNAnswers("I have a paper jam!", 5)[0].topicHeadline)
