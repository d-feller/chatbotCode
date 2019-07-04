import csv
import matplotlib
import matplotlib.pyplot as plt
from config import Config
from latentSemanticIndexingService import LSI_IRService
from cosSimIRService import CosSim_IRService
from doc2VecIRService import Doc2Vec_IRService
from LdaIRService import LDA_IRService
from Document import Document


class TestEvaluation:
    def __init__(self, docCSV):
        self.allHeadlines = Document().allTopics
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
    resTop10 = []
    resTop1 = []

    for k in range(10, 200, 10):
        print("K:", k)
        kList.append(k)
        service = LSI_IRService(config.manualPath, k)
        resTop1.append(tester.startTopNEvaluation(service, 1))
        resTop10.append(tester.startTopNEvaluation(service, 10))
    fig, ax = plt.subplots()
    ax.plot(kList, resTop1, linestyle='--', marker="^")
    ax.plot(kList, resTop10, linestyle='--', marker="o")

    ax.set(xlabel='K', ylabel='P@1[%] P@10[%]',
           title='Precision at 1 and 10 for different K values')
    ax.grid()

    fig.savefig("test.png")
    plt.show()


if __name__ == "__main__":
    config = Config()
    tester = TestEvaluation("../questionAnswerPairs.csv")
    doc2VecService = Doc2Vec_IRService()
    print("Doc2Vec Results:")
    doc2VecTop1 = tester.startTopNEvaluation(doc2VecService, 1)
    doc2VecTop1 = tester.startTopNEvaluation(doc2VecService, 3)
    doc2VecTop10 = tester.startTopNEvaluation(doc2VecService, 10)
    ldaService = LDA_IRService()
    print("LDA Results:")
    ldaTop1 = tester.startTopNEvaluation(ldaService, 1)
    ldaTop1 = tester.startTopNEvaluation(ldaService, 3)
    ldaTop10 = tester.startTopNEvaluation(ldaService, 10)
    cosSimService = CosSim_IRService(config.manualPath)
    print("CosSim Results:")
    cossimTop1 = tester.startTopNEvaluation(cosSimService, 1)
    cossimTop1 = tester.startTopNEvaluation(cosSimService, 3)
    cossimTop10 = tester.startTopNEvaluation(cosSimService, 10)
    lsiService = LSI_IRService(config.manualPath, 50)
    print("LSI Results:")
    lsitop1 = tester.startTopNEvaluation(lsiService, 1)
    lsitop1 = tester.startTopNEvaluation(lsiService, 3)
    lsitop10 = tester.startTopNEvaluation(lsiService, 10)
    # print("ready")
    # plot()
