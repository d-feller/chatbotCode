import csv

import fasttext
from pathlib import Path

from Intent import Intent
from IntentService import IntentService
from preprocess import removeSpecialCharactersAndToLower as prepInput

rawTraining = Path("../classifierTraining.csv")
fastTextTraining = Path("../fastTextTraining.txt")


class fasttext_IntentService(IntentService):
    def __init__(self):
        if Path("./fastTextClassifierModel.bin").exists():
            self.model = fasttext.load_model("./fastTextClassifierModel.bin")
        else:
            self.generateTrainingData()
            self.model = fasttext.train_supervised("../fastTextTraining.txt", wordNgrams=2, dim=300,
                                                   pretrainedVectors="wiki-news-300d-1M.vec")
            self.model.save_model("./fastTextClassifierModel.bin")

    def generateTrainingData(self):
        with rawTraining.open() as input, fastTextTraining.open("w") as output:
            reader = csv.reader(input)
            for line in reader:
                label = line[0]
                text = prepInput(line[1])

                fastTextLine = "__label__{} {}".format(label, text)
                output.write(fastTextLine + "\n")

    def getIntent(self, text):
        intentName = self.model.predict(prepInput(text))[0][0].replace("__label__", "")
        return Intent(intentName)


if __name__ == "__main__":
    c = fasttextClassifier()
    print(c.getIntent("I have to go."))
    print(c.model.test("../fastTextEvalSet.txt"))
