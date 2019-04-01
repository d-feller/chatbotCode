import nltk
import re
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words('english'))

def _removeSpecialCharacters (text):
    newText = re.sub(r"[-()\"#/@;:<>{}+=|~.,!?]", "", text)
    newText = re.sub(r"[^\x00-\x7F]", "", newText)
    return newText

def _removeStopwords(text, stopWords=STOPWORDS):
    filtered = []
    for word in text:
        if word not in stopWords:
            filtered.append(word)
    return filtered

def _tokenize(text):
    return nltk.word_tokenize(text)

def preprocessTextInput(text, stopwords=STOPWORDS):
    return removeStopwords(_tokenize(_removeSpecialCharacters(text)), stopwords) 

