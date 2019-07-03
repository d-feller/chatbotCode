class Intent:
    allIntents = ["Greeting", "InformationRetrieval", "Farewell", "UNKNOWN"]

    def __init__(self, intent="Greeting"):
        if intent not in self.allIntents:
            print("The intent must be one of the following: ", str(self.allIntents))
        self.name = intent
