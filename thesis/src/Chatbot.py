from fasttext_IntentService import fasttext_IntentService
from latentSemanticIndexingService import LSI_IRService
from LdaIRService import LDA_IRService
import random
from Answer import Answer


class Chatbot:
    GREETINGS = ["Hi, how are you?", "Hello there!", "Hey, what's up?", "Hey! I am glad to see you!"]
    FAREWELLS = ["See you next time!", "Ciao!", "Bye Bye!"]

    def __init__(self):
        self.intentService = fasttext_IntentService()
        #self.informationRetrievalService = LSI_IRService()
        self.informationRetrievalService = LDA_IRService()

    def getAnswer(self, query):
        intent = self.intentService.getIntent(query)
        print("Intent before if else:", intent.name)
        if intent.name == "Greeting":
            print("Intent:", intent.name)
            text = random.choice(self.GREETINGS)
            return Answer(0, text, text, "Greeting")
        elif intent.name == "InformationRetrieval":
            print("Intent:", intent.name)
            answer = self.informationRetrievalService.getTopNAnswers(query, 1)
            return answer[0]
        elif intent.name == "Farewell":
            print("Intent:", intent.name)
            text = random.choice(self.FAREWELLS)
            return Answer(0, text, text, "Farewell")
