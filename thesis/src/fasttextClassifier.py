import csv

import fasttext
from pathlib import Path

from Intent import Intent
from IntentService import IntentService
from preprocess import removeSpecialCharactersAndToLower as prepInput

rawTraining = Path("../classifierTraining.csv")
fastTextTraining = Path("../fastTextTraining.txt")


class fasttextClassifier(IntentService):
    def __init__(self):
        if Path("./preTrainedModel.bin").exists():
            self.model = fasttext.load_model("./preTrainedModel.bin")
        else:
            self.generateTrainingData()
            self.model = fasttext.train_supervised("../fastTextTraining.txt", wordNgrams=2, dim=300,
                                                   pretrainedVectors="word2Vec.vec")
            self.model.save_model("./fastTextClassifierModel")

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
