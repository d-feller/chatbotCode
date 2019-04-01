import preprocess as prep
import scipy
import math
import numpy as np
import json
import collections
import os


fileToWords = prep.getFileToWordsDict()
filesList = list(fileToWords.keys())
wordToNumber = collections.OrderedDict()
i = 0
for value in fileToWords.values():
	for word in value:
		if word in wordToNumber:
			continue
		else:
			wordToNumber[word] = i 
			i += 1

termDocArray = []
for words in fileToWords.values():
	termDocVector = np.zeros(len(wordToNumber.values())) 
	for word in words:
		termDocVector[wordToNumber[word]] += 1
	# Exclude Pages with no words
	if all(v == 0 for v in termDocVector):
		continue
	termDocArray.append(termDocVector)

fileToWordNumber = {}
for key, value in fileToWords.items():
	newValue = []
	for word in value:
		newValue.append(wordToNumber[word])
	fileToWordNumber[key] = newValue

def calcWeight (word, document, allDocuments):
	totalNumOfDocuments = len(allDocuments)
	termFreq = calcTermFrequency(word, document)
	numOfOcc = calcNumOfOccurencesInCollection(word, allDocuments)
	if termFreq > 0:
		return (1 + math.log10(totalNumOfDocuments/numOfOcc))

	return 0

def calcTermFrequency (word, document):
	numOfOccurences = 0
	for token in document:
		if word == token:
			numOfOccurences += 1
	return numOfOccurences

def calcNumOfOccurencesInCollection (word, allDocs):
	numOfOccurences = 0
	for doc in allDocs:
		if word in doc:
			numOfOccurences += 1
	return numOfOccurences

def calcAllDocWordVectos():
	fileToWordVector = {}
	allDocuments = fileToWordNumber.values()
	for key, doc in fileToWordNumber.items():
		documentWordVector = []
		for word in wordToNumber.values():
			documentWordVector.append(calcWeight(word, doc, allDocuments))
		fileToWordVector[key] = documentWordVector
	return fileToWordVector

def fetchOrCalcAllDocWordVectors():
	fileToWordVector = {}
	if os.path.isfile('./weights.json'):
		with open('./weights.json', 'r') as file:
			fileToWordVector = json.loads(file.read())
	else:
		fileToWordVector = calcAllDocWordVectos()
		with open('./weights.json', 'w+') as file:
			file.write(json.dumps(fileToWordVector))
	return fileToWordVector

def getVectorFromQuery(query):
	query = query.lower().split(' ')
	vec = np.zeros(len(wordToNumber.values()))
	for word in query:
		if word in wordToNumber:
			vec[wordToNumber[word]] += 1
	return vec

termDocumentMatrix = np.matrix(termDocArray)
termDocumentMatrix = termDocumentMatrix.T
u, s, vh = np.linalg.svd(termDocumentMatrix, full_matrices=False)
S = np.diag(s)
print(S)
print(u.shape, S.shape, vh.shape)
# ersetzen durch variable K
uk = u[:, :10]
Sk = S[:10, :10]
vhk = vh[:10, :]

queryVector = getVectorFromQuery("Set up a Bluetooth wireless connection ")
qVector = np.array(queryVector)
newQueryVector = np.dot(np.dot(qVector.T,uk), np.linalg.inv(Sk))

result = []
for vec in vhk.T:
	result.append(1. - scipy.spatial.distance.cosine(newQueryVector, vec))

result = np.array(result)
print(result)
print( np.argmax(result), result[np.argmax(result)])
print(filesList[np.argmax(result)])
