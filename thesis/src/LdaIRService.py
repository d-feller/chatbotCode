from Document import Document
import gensim
from config import Config
from pathlib import Path
from Answer import Answer
from IRService import IRService
from gensim.corpora.dictionary import Dictionary
import numpy as np
from scipy.stats import entropy
from preprocess import preprocessTextInput as prepInput

c = Config()


class LDA_IRService(IRService):
    def __init__(self):
        super()
        self.document = Document()
        tokens = self.document.docList
        self.dictionary = Dictionary(tokens)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in tokens]
        self.corpusTFIDf = gensim.models.TfidfModel(self.corpus)[self.corpus]
        self.model = gensim.models.LdaMulticore(self.corpus, id2word=self.dictionary)
        self.model_tfidf = gensim.models.LdaMulticore(self.corpusTFIDf, id2word=self.dictionary)
        self.doc_topic_dist = np.zeros([len(self.corpus), self.model.num_topics])
        self.doc_topic_dist_tfidf = np.zeros([len(self.corpusTFIDf), self.model_tfidf.num_topics])
        for i, doc in enumerate(self.model[self.corpus]):
            for tup in doc:
                topicIndex = tup[0]
                topicValue = tup[1]
                self.doc_topic_dist[i][topicIndex] = topicValue
        for i, doc in enumerate(self.model_tfidf[self.corpusTFIDf]):
            for tup in doc:
                topicIndex = tup[0]
                topicValue = tup[1]
                self.doc_topic_dist_tfidf[i][topicIndex] = topicValue

    def getTopNAnswers(self, query, n):
        htmlOutput = []
        answers = []
        indeces = self.get_most_similar_documents(query, self.doc_topic_dist, n)
        for i in indeces:
            text = self.document.rawDocList[i]
            resultNodes = self.document.nodeList[i]
            topic = resultNodes[0].topic.strip()
            for node in resultNodes:
                htmlOutput.append(str(node.data))
            answers.append(Answer(2, text, htmlOutput, topic))
        return answers

    def jensen_shannon(self, query, matrix):
        """
        This function implements a Jensen-Shannon similarity
        between the input query (an LDA topic distribution for a document)
        and the entire corpus of topic distributions.
        It returns an array of length M where M is the number of documents in the corpus
        """
        # lets keep with the p,q notation above
        p = query[None, :].T  # take transpose
        q = matrix.T  # transpose matrix
        m = 0.5 * (p + q)
        return np.sqrt(0.5 * (entropy(p, m) + entropy(q, m)))

    def get_most_similar_documents(self, query, k):
        """
        This function implements the Jensen-Shannon distance above
        and returns the top k indices of the smallest jensen shannon distances
        """
        bowVec = self.dictionary.doc2bow(prepInput(query))
        newDocDistro = np.zeros(self.model.num_topics)
        for tup in self.model.get_document_topics(bow=bowVec):
            topicIndex = tup[0]
            topicValue = tup[1]
            newDocDistro[topicIndex] = topicValue
        sims = self.jensen_shannon(newDocDistro, self.doc_topic_dist)  # list of jensen shannon distances
        return sims.argsort()[:k]  # the top k positional index of the smallest Jensen Shannon distances


if __name__ == "__main__":
    s = LDA_IRService()
    print(s.getAnswer("How to cancel the print job?").text)
