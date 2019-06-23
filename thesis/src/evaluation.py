import csv

from config import config
from latentSemanticIndexingService import LSI_Service


class TestEvaluation:
    def __init__(self, docCSV, serviceToTest):
        self.questions = []
        self.expectedPages = []
        self.expectedTopicHeadline = []
        with open(docCSV) as f:
            reader = csv.reader(f)
            # Skip Header
            next(reader)
            for row in reader:
                self.expectedTopicHeadline.append(row[0])
                self.expectedPages.append(list(map(int, row[1].split(","))))
                self.questions.append(row[2:])

    def startEvaluation(self, retrievalMethod):
        print("Evaluation Started!")
        for i in range(len(self.expectedTopicHeadline)):
            for question in self.questions[i]:
                if question is "":
                    continue
                print(question)
                print("expected section :",
                      self.expectedTopicHeadline[i], ", but got: ", retrievalMethod.getAnswer(question).topicHeadline)
        print("Evaluation finished!")


if __name__ == "__main__":
    config = config()
    service = LSI_Service(config.manualPath)
    tester = TestEvaluation("../questionAnswerPairs.csv", service)
    print(tester.startEvaluation(service))
