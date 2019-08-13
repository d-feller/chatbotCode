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
        resultsIndeces = np.argsort(npDistances)[:n]
        for i in resultsIndeces:
            topResultNodes = self.nodes[i]
            for node in topResultNodes:
                htmlOutput.append(str(node.data))
                textOutput.append(node.data.getText())
            topResultTopicHeadline = topResultNodes[0].topic
            answers.append(Answer(2, textOutput, "".join(htmlOutput), topResultTopicHeadline))
        return answers


if __name__ == "__main__":
    s = neuralEmb_IRService()
    print(s.getTopNAnswers("I have a paper jam!", 5)[0].topicHeadline)
