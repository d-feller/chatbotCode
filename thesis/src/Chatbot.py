from IntentService import IntentService
from latentSemanticIndexingService import LSI_IRService
import random
from Answer import Answer


class Chatbot:
    GREETINGS = ["Hi, how are you?", "Hello there!", "Hey, what's up?", "Hey! I am glad to see you!"]
    FAREWELLS = ["See you next time!", "Ciao!", "Bye Bye!"]

    def __init__(self):
        self.intentService = IntentService()
        self.informationRetrievalService = LSI_IRService()

    def getAnswer(self, query):
        intent = self.intentService.getIntent(query)
        if intent.name is "Greeting":
            text = random.choice(self.GREETINGS)
            return Answer(0, text, text, "Greeting")
        elif intent.name is "InformationRetrieval":
            answer = self.informationRetrievalService.getAnswer(query)
            return answer
        elif intent.name is "Farewell":
            text = random.choice(self.FAREWELLS)
            return Answer(0, text, text, "Farewell")
