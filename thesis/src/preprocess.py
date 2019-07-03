import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

STOPWORDS = set(stopwords.words('english'))
PS = PorterStemmer()

def preprocessTextInput(text, stopwords=STOPWORDS):
    return _stem(_removeStopwords(_tokenize(removeSpecialCharactersAndToLower(text)), stopwords))

def removeSpecialCharactersAndToLower (text):
    newText = re.sub(r"[-()\"#/@;:<>{}+=|~.,!?]", " ", text)
    newText = re.sub(r"[^\x00-\x7F]", " ", newText)
    newText = newText.lower()
    return newText

def _removeStopwords(text, stopWords=STOPWORDS):
    filtered = []
    for word in text:
        if word not in stopWords:
            filtered.append(word)
    return filtered

def _tokenize(text):
    return nltk.word_tokenize(text)

def _stem(text):
    newText = []
    for w in text:
        newText.append(PS.stem(w))
    return newText


