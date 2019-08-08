import csv
import matplotlib
import matplotlib.pyplot as plt
from config import Config
from latentSemanticIndexingService import LSI_IRService
from cosSimIRService import CosSim_IRService
from doc2VecIRService import Doc2Vec_IRService
from LdaIRService import LDA_IRService
from Document import Document
import random
from neuralEmbIRService import neuralEmb_IRService
from pathlib import Path
import os


class TestEvaluation:
    def __init__(self, docCSV):
        self.doc = Document()
        self.allHeadlines = self.doc.allTopics
        self.questions = []
        self.expectedPages = []
        self.expectedTopicHeadline = []
        with open(docCSV) as f:
            reader = csv.reader(f)
            # Skip Header
            next(reader)
            questions = []
            for row in reader:
                self.expectedTopicHeadline.append(row[0])
                self.expectedPages.append(list(map(int, row[1].split(","))))
                questions.append(list(map(str.strip, row[2:])))
            self.questions = questions

    def startTopNRandom(self, n):
        total = 0
        correct = 0
        for i in range(len(self.expectedTopicHeadline)):
            for question in self.questions[i]:
                if question.strip():
                    topNHeadlines = []
                    answers = []
                    for j in range(n):
                        answers.append(random.choice(self.doc.allTopics))
                    for answer in answers:
                        topNHeadlines.append(answer)
                    if self.expectedTopicHeadline[i].strip() in topNHeadlines:
                        correct += 1
                    total += 1
        print("Top {} Evaluation finished! ".format(n) + str(correct) + "/" + str(total) + "=" + str(
            correct * 100 / total) + "% correct.")
        return correct * 100 / total

    def startTopNEvaluation(self, retrievalMethod, n):
        total = 0
        correct = 0
        for i in range(len(self.expectedTopicHeadline)):
            for question in self.questions[i]:
                if question.strip():
                    topNHeadlines = []
                    answers = retrievalMethod.getTopNAnswers(question, n)
                    for answer in answers:
                        topNHeadlines.append(answer.topicHeadline.strip())
                    # print("question:", question)
                    # print("expect:", self.expectedTopicHeadline[i])
                    # print("list:", topNHeadlines)
                    if self.expectedTopicHeadline[i].strip() in topNHeadlines:
                        correct += 1
                    total += 1
        print("Top {} Evaluation finished! ".format(n) + str(correct) + "/" + str(total) + "=" + str(
            correct * 100 / total) + "% correct.")
        return correct * 100 / total


def plot():
    config = Config()
    tester = TestEvaluation("../questionAnswerPairs.csv")
    kList = []
    resTop1 = []
    resTop3 = []
    resTop10 = []

    for k in range(25, 76, 1):
        print("K:", k)
        kList.append(k)
        service = LSI_IRService(config.manualPath, k)
        resTop1.append(tester.startTopNEvaluation(service, 1))
        resTop3.append(tester.startTopNEvaluation(service, 3))
        resTop10.append(tester.startTopNEvaluation(service, 10))
    fig, ax = plt.subplots()
    ax.plot(kList, resTop1, linestyle='--', marker="^")
    ax.plot(kList, resTop3, linestyle='--', marker="+")
    ax.plot(kList, resTop10, linestyle='--', marker="o")

    ax.set(xlabel='K', ylabel='P@1[%] P@10[%]',
           title='Precision at 1, 3 and 10 for different K values')
    ax.grid()

    fig.savefig("LSIrampe25-75.png")
    plt.show()


def plotLDAKTopics():
    config = Config()
    tester = TestEvaluation("../questionAnswerPairs.csv")
    kList = []
    resTop10 = []
    resTop3 = []
    resTop1 = []

    for k in range(5, 105, 5):
        if Path(config.ldaModelFile).exists():
            os.remove(config.ldaModelFile)
        print("K:", k)
        kList.append(k)
        service = LDA_IRService(k)
        resTop1.append(tester.startTopNEvaluation(service, 1))
        resTop3.append(tester.startTopNEvaluation(service, 3))
        resTop10.append(tester.startTopNEvaluation(service, 10))
    fig, ax = plt.subplots()
    ax.plot(kList, resTop1, linestyle='--', marker="^")
    ax.plot(kList, resTop3, linestyle='-.', marker="+")
    ax.plot(kList, resTop10, linestyle='--', marker="o")
    ax.set(xlabel='Number of topics', ylabel='P@1[%] P@3[%] P@10[%]',
           title='Precision at 1, 3 and 10 for K topics')
    ax.grid()
    plt.xticks(range(1, 21, 1))

    fig.savefig("LDA5-100Ktopics.png")
    plt.show()
def plotLDA():
    config = Config()
    tester = TestEvaluation("../questionAnswerPairs.csv")
    kList = []
    resTop10 = []
    resTop3 = []
    resTop1 = []

    for k in range(1, 21, 1):
        if Path(config.ldaModelFile).exists():
            os.remove(config.ldaModelFile)
        print("K:", k)
        kList.append(k)
        service = LDA_IRService(40)
        resTop1.append(tester.startTopNEvaluation(service, 1))
        resTop3.append(tester.startTopNEvaluation(service, 3))
        resTop10.append(tester.startTopNEvaluation(service, 10))
    fig, ax = plt.subplots()
    ax.plot(kList, resTop1, linestyle='--', marker="^")
    ax.plot(kList, resTop3, linestyle='-.', marker="+")
    ax.plot(kList, resTop10, linestyle='--', marker="o")
    ax.set(xlabel='Number of topics', ylabel='P@1[%] P@3[%] P@10[%]',
           title='Precision at 1, 3 and 10 for K topics')
    ax.grid()
    plt.xticks(range(1, 21, 1))

    fig.savefig("LDA5-100Ktopics.png")
    plt.show()

if __name__ == "__main__":
    config = Config()
    tester = TestEvaluation("../questionAnswerPairs.csv")
    # doc2VecService = Doc2Vec_IRService()
    # print("Doc2Vec Results:")
    # doc2VecTop1 = tester.startTopNEvaluation(doc2VecService, 1)
    # doc2VecTop3 = tester.startTopNEvaluation(doc2VecService, 3)
    # doc2VecTop10 = tester.startTopNEvaluation(doc2VecService, 10)
    # ldaService = LDA_IRService()
    # print("LDA Results:")
    # ldaTop1 = tester.startTopNEvaluation(ldaService, 1)
    # ldaTop3 = tester.startTopNEvaluation(ldaService, 3)
    # ldaTop10 = tester.startTopNEvaluation(ldaService, 10)
    # cosSimService = CosSim_IRService(config.manualPath)
    # print("CosSim Results:")
    # cossimTop1 = tester.startTopNEvaluation(cosSimService, 1)
    # cossimTop3 = tester.startTopNEvaluation(cosSimService, 3)
    # cossimTop10 = tester.startTopNEvaluation(cosSimService, 10)
    # lsiService = LSI_IRService(config.manualPath, 50)
    # print("LSI Results:")
    # lsitop1 = tester.startTopNEvaluation(lsiService, 1)
    # lsitop3 = tester.startTopNEvaluation(lsiService, 3)
    # lsitop10 = tester.startTopNEvaluation(lsiService, 10)
    # print("Random Results:")
    # tester.startTopNRandom(1)
    # tester.startTopNRandom(3)
    # tester.startTopNRandom(10)
    # print("Neural Embedding Results:")
    # nEmbService = neuralEmb_IRService()
    # tester.startTopNEvaluation(nEmbService, 1)
    # tester.startTopNEvaluation(nEmbService, 3)
    # tester.startTopNEvaluation(nEmbService, 10)
    plotLDA()
    # plot()
