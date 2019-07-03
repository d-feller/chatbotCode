from Document import Document
import gensim
from config import Config
from pathlib import Path
from Answer import Answer
from IRService import IRService
from preprocess import preprocessTextInput as prepInput

c = Config()

class Doc2VecIRService(IRService):
    def __init__(self):
        super()
        self.model = gensim.models.doc2vec.Doc2Vec(vector_size=100, min_count=1, epochs=100)
        self.document = Document()
        if not Path(c.doc2VecModel).exists():
            docs = self.document.docList
            trainCorpus = list(self._readCorpus(docs))
            self.model.build_vocab(trainCorpus)
            self.model.train(trainCorpus, total_examples=self.model.corpus_count, epochs=self.model.epochs)
            self.model.save("./doc2VecModel")
        else:
            self.model = gensim.models.Doc2Vec.load(c.doc2VecModel)

    def _readCorpus(self, docList):
        for i, doc in enumerate(docList):
            yield gensim.models.doc2vec.TaggedDocument(doc, [i])

    def getTopNAnswers(self, query, n):
        queryVector = self.model.infer_vector(prepInput(query))
        sims = self.model.docvecs.most_similar([queryVector], topn=len(self.model.docvecs))
        results = []
        for item in sims:
            text = self.document.docList[item[0]]
            topic = self.document.allTopics[item[0]].strip()
            results.append(Answer(2, text, "html", topic))
        return results[:n]

if __name__ == "__main__":
    s = Doc2VecIRService()
    print(s.getAnswer("My print is just in black and white").topicHeadline)
