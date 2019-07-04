from Document import Document
import gensim
from config import Config
from pathlib import Path
from Answer import Answer
from IRService import IRService
from preprocess import preprocessTextInput as prepInput
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

c = Config()

class Doc2Vec_IRService(IRService):
    def __init__(self):
        super()
        self.document = Document()
        if not Path(c.doc2VecModel).exists():
            docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(self.document.docList)]
            self.model = Doc2Vec(vector_size=100, window=2, min_count=1, workers=4, epochs=40)
            self.model.build_vocab(docs)
            self.model.train(docs, total_examples=self.model.corpus_count, epochs=self.model.epochs)
            self.model.save("./doc2VecModel")
        else:
            self.model = Doc2Vec.load(c.doc2VecModel)


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
    s = Doc2Vec_IRService()
    print(s.getTopNAnswers("My print is just in black and white", 1)[0].topicHeadline)
