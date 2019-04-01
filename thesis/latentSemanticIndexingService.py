import preprocess as prep
import scipy
import math
import numpy as np
import json
import collections
import os
from parseHTMLtoTree import getTree
from anytree.iterators import PreOrderIter

filepath = './manuals/html/printer/printerManual.html'
tree = getTree(filepath)

firstHeadline = tree.children[0]
names = [node.data.getText() for node in PreOrderIter(firstHeadline)]
print(names)

def calcWeight (word, document, allDocuments):
	totalNumOfDocuments = len(allDocuments)
	termFreq = _calcTermFrequency(word, document)
	numOfOcc = _calcNumOfOccurencesInCollection(word, allDocuments)
	if termFreq > 0:
		return (1 + math.log10(totalNumOfDocuments/numOfOcc))
	return 0

def _calcTermFrequency (word, document):
	numOfOccurences = 0
	for token in document:
		if word == token:
			numOfOccurences += 1
	return numOfOccurences

def _calcNumOfOccurencesInCollection (word, allDocs):
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

# termDocumentMatrix = np.matrix(termDocArray)
# termDocumentMatrix = termDocumentMatrix.T
# u, s, vh = np.linalg.svd(termDocumentMatrix, full_matrices=False)
# S = np.diag(s)
# print(S)
# print(u.shape, S.shape, vh.shape)
# # ersetzen durch variable K
# uk = u[:, :10]
# Sk = S[:10, :10]
# vhk = vh[:10, :]
# 
# queryVector = getVectorFromQuery("Set up a Bluetooth wireless connection ")
# qVector = np.array(queryVector)
# newQueryVector = np.dot(np.dot(qVector.T,uk), np.linalg.inv(Sk))
# 
# result = []
# for vec in vhk.T:
# 	result.append(1. - scipy.spatial.distance.cosine(newQueryVector, vec))
# 
# result = np.array(result)
# print(result)
# print( np.argmax(result), result[np.argmax(result)])
# print(filesList[np.argmax(result)])
