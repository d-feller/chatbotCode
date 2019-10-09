import gensim
import numpy as np
from gensim.corpora.dictionary import Dictionary
from scipy.stats import entropy

from Answer import Answer
from Document import Document
from IRService import IRService
from config import Config
from preprocess import preprocessTextInput as prepInput
from pathlib import Path
c = Config()
import matplotlib.pyplot as plt
# Gensim
import gensim
from gensim.models import CoherenceModel

class LDA_IRService(IRService):
    def __init__(self, numTopics=32):
        super()
        self.document = Document()
        self.tokens = self.document.docList
        self.dictionary = Dictionary(self.tokens)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.tokens]
        self.headline_corpus = self.dictionary.doc2bow(self.document.allTopics)
        if Path("LDAmodel").exists():
            self.model = gensim.models.LdaModel.load("LDAmodel")
        else:
            self.model = gensim.models.LdaModel(
                self.corpus,
                id2word=self.dictionary,
                num_topics=numTopics,
                iterations=300,
                alpha='auto',
                random_state=None,
                passes=10,
                per_word_topics=False)
            self.model.save("LDAmodel")
        self.doc_topic_dist = np.zeros([len(self.corpus), self.model.num_topics])
        for i, doc in enumerate(self.model[self.corpus]):
            for tup in doc:
                topicIndex = tup[0]
                topicValue = tup[1]
                self.doc_topic_dist[i][topicIndex] = topicValue

        self.topic_dist = np.zeros([len(self.corpus), self.model.num_topics])
        for i, tup in enumerate(self.model[self.headline_corpus]):
            topicIndex = tup[0]
            topicValue = tup[1]
            self.topic_dist[i][topicIndex] = topicValue

    def getTopNAnswers(self, query, n):
        htmlOutput = []
        answers = []
        indeces = self.get_most_similar_documents(query, n)
        headlineIndeces = self.compareToTopics(query, n)
        for i in range(len(indeces)):
            a = indeces[i]
            b = headlineIndeces[i]
            res = a if a > b else b
            text = self.document.rawDocList[b]
            resultNodes = self.document.nodeList[b]
            topic = resultNodes[0].topic.strip()
            for node in resultNodes:
                htmlOutput.append(str(node.data))
            answers.append(Answer(2, text, "".join(htmlOutput), topic))
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

    def compareToTopics(self, query, k):
        bowVec = self.dictionary.doc2bow(prepInput(query))
        newDocDistro = np.zeros(self.model.num_topics)
        for tup in self.model.get_document_topics(bow=bowVec):
            topicIndex = tup[0]
            topicValue = tup[1]
            newDocDistro[topicIndex] = topicValue
        sims = self.jensen_shannon(newDocDistro, self.topic_dist)  # list of jensen shannon distances
        return sims.argsort()[:k]  # the top k positional index of the smallest Jensen Shannon distances

    def compute_coherence_values(self, limit, start=2, step=3):
        """
        Compute c_v coherence for various number of topics

        Parameters:
        ----------
        dictionary : Gensim dictionary
        corpus : Gensim corpus
        texts : List of input texts
        limit : Max num of topics

        Returns:
        -------
        model_list : List of LDA topic models
        coherence_values : Coherence values corresponding to the LDA model with respective number of topics
        """
        coherence_values = []
        model_list = []
        for num_topics in range(start, limit, step):
            model = gensim.models.LdaModel(self.corpus, id2word=self.dictionary, num_topics=num_topics,
                                                    iterations=100, alpha='auto', passes=10, random_state=None,
                                                    update_every=1,
                                                    per_word_topics=True
                                                    )
            model_list.append(model)
            coherencemodel = CoherenceModel(model=model, texts=self.corpus, dictionary=self.dictionary, coherence='c_v')
            coherence_values.append(coherencemodel.get_coherence())

        return model_list, coherence_values

if __name__ == "__main__":
    s = LDA_IRService()


def showGraph():
    s = LDA_IRService()
    # Show graph
    limit = 124
    start = 2
    step = 4
    model_list, coherence_values = s.compute_coherence_values(start=start, limit=limit, step=step)
    x = range(start, limit, step)
    plt.plot(x, coherence_values)
    plt.grid()
    plt.xlabel("Number of Topics")
    plt.ylabel("Coherence score")
    plt.show()
