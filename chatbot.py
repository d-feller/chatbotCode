import numpy as np
import tensorflow as tf
import re
import time

lines = open('movie_lines.txt', encoding = 'utf-8', errors='ignore').read().split('\n')
conversations = open('movie_conversations.txt', encoding = 'utf-8', errors='ignore').read().split('\n')

idToLine = {}
for line in lines: 
    _line = line.split(' +++$+++ ')
    if len(_line) == 5:
        idToLine[_line[0]] = _line[4]

conversationsIds = []
for conversation in conversations[:-1]:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace('\'','').replace(' ','')
    conversationsIds.append(_conversation.split(','))

questions = []
answers = []
for conversation in conversationsIds:
    for i in range(len(conversation) - 1):
        questions.append(idToLine[conversation[i]])
        answers.append(idToLine[conversation[i+1]])
        
def cleanText(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"don't", "do not", text)
		text = re.sub(r"[-()\"#/@;:<>{}+=|~.?,!]", "do not", text)
		return text
