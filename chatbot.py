import numpy as np
import tensorflow as tf
import re
import time

lines = open('movie_lines.txt', encoding='utf-8', errors='ignore').read().split('\n')
conversations = open('movie_conversations.txt', encoding='utf-8', errors='ignore').read().split('\n')

# ---------------------------------------
# -------- Data Preprocessing -----------
# ---------------------------------------

idToLine = {}
for line in lines:
	_line = line.split(' +++$+++ ')
	if len(_line) == 5:
		idToLine[_line[0]] = _line[4]

conversationsIds = []
for conversation in conversations[:-1]:
	_conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace('\'', '').replace(' ','')
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
	text = re.sub(r"it's", "it am", text)
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
	text = re.sub(r"\*", "", text)
	text = re.sub(r"[-()\"#/@;:<>{}+=|~.,!?]", "", text)
	return text

cleanQuestions = []
for question in questions:
	cleanQuestions.append(cleanText(question))

cleanAnswers = []
for answer in answers:
	cleanAnswers.append(cleanText(answer))

wordToCount = {}
for question in cleanQuestions:
	for word in question.split():
		if word not in wordToCount:
			wordToCount[word] = 1
		else:
			wordToCount[word] += 1

for answer in cleanAnswers:
	for word in answer.split():
		if word not in wordToCount:
			wordToCount[word] = 1
		else:
			wordToCount[word] += 1

# ---------------------------------------

threshold = 20 # 5% of the least frequent words

questionWordsToInt = {}
wordNumber = 0
for word, count in wordToCount.items():
	if count >= threshold:
		questionWordsToInt[word] = wordNumber
		wordNumber += 1

answerWordsToInt = {}
wordNumber = 0
for	word, count in wordToCount.items():
	if count >= threshold:
		answerWordsToInt[word] = wordNumber
		wordNumber += 1

# Adding the last tokens to these two dictionaries
tokens = ['<PAD>','<EOS>','<OUT>','<SOS>']
for token in tokens:
	questionWordsToInt[token] = len(questionWordsToInt) + 1

for token in tokens:
	answerWordsToInt[token] = len(answerWordsToInt) + 1

answersIntToWord = {wInt : w for w, wInt in answerWordsToInt.items()}

# Adding the End Of String token to the end of every answer
for i in range(len(cleanAnswers)):
	cleanAnswers[i] += ' <EOS>'

# Translate all the questions and the answers into integers
# and replace all the words that were filtered out by <OUT>
questionsIntoInt = []
for question in cleanQuestions:
	ints = []
	for word in question.split():
		if word not in questionWordsToInt:
			ints.append(questionWordsToInt['<OUT>'])
		else:
			ints.append(questionWordsToInt[word])
	questionsIntoInt.append(ints)

answersIntoInt = []
for answer in cleanAnswers:
	ints = []
	for word in answer.split():
		if word not in answerWordsToInt:
			ints.append(answerWordsToInt['<OUT>'])
		else:
			ints.append(answerWordsToInt[word])
	answersIntoInt.append(ints)


# Sort the questions and anwsers by the length of questions
sortedCleanQuestions = []
sortedCleanAnswers = []

for length in range(1, 25 + 1):
	for i in enumerate(questionsIntoInt):
		if len(i[1]) == length:
			sortedCleanQuestions.append(questionsIntoInt[i[0]])
			sortedCleanAnswers.append(answersIntoInt[i[0]])


# ---------------------------------------
# ----- Build the SEQ2SEQ model ---------
# ---------------------------------------

def modelInputs():
	inputs = tf.placeholder(tf.int32,	[None, None], name = 'input')
	targets = tf.placeholder(tf.int32,	[None, None], name = 'target')
	lr = tf.placeholder(tf.float32, name = 'learning_rate')
	keepProb = tf.placeholder(tf.float32, name = 'keepProb')
	return inputs, targets, lr, keepProb

# Preprocessing targets
def preprocessTargets(targets, wordToInt, batchSize):
	leftSide = tf.fill([batchSize, 1], wordToInt['<SOS>'])
	rightSide = tf.strided_slice(targets, [0,0], [batchSize, -1], [1,1])
	preprocessedTargets = tf.concat([leftSide, rightSide], 1)
	return preprocessedTargets

# Creating the Encoder RNN Layer
def encoderRNNLayer(rnnInputs, rnnSize, numLayers, keepProb, sequenceLength):
	lstm = tf.contrib.rnn.BasicLSTMCell(rnnSize)
	lstmDropout = tf.contrib.rnn.DropoutWrapper(lstm, input_keep_prob = keepProb)
	encoderCell = tf.contrib.rnn.MultiRNNCell([lstmDropout] * numLayers)
	_, encoderState = tf.nn.bidirectional_dynamic_rnn(
			cell_fw = encoderCell,
			cell_bw = encoderCell,
			sequence_length = sequenceLength,
			inputs = rnnInputs,
			dtype = tf.float32)
	return encoderState

def decodeTrainingSet(encoderState, decoderCell, decoderEmbeddedInput,
		sequenceLength,
		decodingScope,
		outputFunction,
		keepProb,
		batchSize):

	attentionStates = tf.zeros([batchSize, 1, decoderCell.output_size])

	attentionKeys, attentionValues, attentionScoreFunction, attentionConstructFunction = tf.contrib.seq2seq.prepare_attention(
			attentionStates,
			attention_option='bahdanau',
			num_units= decoderCell.output_size)

	trainingDecoderFunction =	tf.contrib.seq2seq.attention_decoder_fn_train(
			encoderState[0],
			attentionKeys,
			attentionValues,
			attentionScoreFunction,
			attentionConstructFunction,
			name = 'attn_dec_train')
	decoderOutput, _, _ = tf.contrib.seq2seq.dynamic_rnn_decoder(decoderCell,
			trainingDecoderFunction,
			decoderEmbeddedInput,
			sequenceLength,
			scope = decodingScope)

	decoderOutputDropout = tf.nn.dropout(decoderOutput, keepProb)
	return outputFunction(decoderOutputDropout)

# Decoding the test/validation set

def decodeTestSet(encoderState, decoderCell, decoderEmbeddingsMatrix,
		sosID,
		eosID,
		maximumLength,
		numWords,
		sequenceLength,
		decodingScope,
		outputFunction,
		keepProb,
		batchSize):

	attentionStates = tf.zeros([batchSize, 1, decoderCell.output_size])

	attentionKeys, attentionValues, attentionScoreFunction, attentionConstructFunction = tf.contrib.seq2seq.prepare_attention(
			attentionStates,
			attention_option='bahdanau',
			num_units= decoderCell.output_size)

	testDecoderFunction =	tf.contrib.seq2seq.attention_decoder_fn_inference(
			outputFunction,
			encoderState[0],
			attentionKeys,
			attentionValues,
			attentionScoreFunction,
			attentionConstructFunction,
			decoderEmbeddingsMatrix,
			sosID,
			eosID,
			maximumLength,
			numWords,
			name = 'attn_dec_inf')

	testPredictions, _, _ = tf.contrib.seq2seq.dynamic_rnn_decoder(decoderCell,
			testDecoderFunction,
			scope = decodingScope)

	return testPredictions

# Create the Decode RNN Layer
def decoderRNNLayer(decoderEmbeddedInput, decoderEmbeddingsMatrix, encoderState,
		numWords,
		sequenceLength,
		rnnSize,
		numLayers,
		wordToInt,
		keepProb,
		batchSize):
	with tf.variable_scope('decoding') as decodingScope:
		lstm = tf.contrib.rnn.BasicLSTMCell(rnnSize)
		lstmDropout = tf.contrib.rnn.DropoutWrapper(lstm, input_keep_prob = keepProb)
		decoderCell = tf.contrib.rnn.MultiRNNCell([lstmDropout] * numLayers)
		weigths = tf.truncated_normal_initializer(stddev = 0.1)
		biases = tf.zeros_initializer()
		outputFunction = lambda x: tf.contrib.layers.fully_connected(
				x,
				numWords,
				None,
				scope = decodingScope,
				weights_initializer = weigths,
				biases_initializer = biases)
		trainingPredictions = decodeTrainingSet(encoderState, decoderCell,
				decoderEmbeddedInput,
				sequenceLength,
				decodingScope,
				outputFunction,
				keepProb,
				batchSize)
		decodingScope.reuse_variables()
		testPredictions = decodeTestSet(encoderState, decoderCell, decoderEmbeddingsMatrix,
				wordToInt['<SOS>'],
				wordToInt['<EOS>'],
				sequenceLength -1,
				numWords,
				decodingScope,
				outputFunction,
				keepProb,
				batchSize)
	return trainingPredictions, testPredictions

def seqToSeqModel(inputs, targets, keepProb, batchSize, sequenceLength,
		answersNumWords,
		questionsNumWords,
		encoderEmbeddingSize,
		decoderEmbeddingSize,
		rnnSize,
		numLayers,
		questionWordsToInt):
	encoderEmbeddedInput = tf.contrib.layers.embed_sequence(inputs, answersNumWords + 1,
			encoderEmbeddingSize,
			initializer = tf.random_uniform_initializer(0, 1))
	encoderState = encoderRNNLayer(encoderEmbeddedInput, rnnSize, numLayers,
			keepProb,
			sequenceLength)
	preprocessedTargets = preprocessTargets(targets, questionWordsToInt, batchSize)
	decoderEmbeddingsMatrix = tf.Variable(tf.random_uniform([questionsNumWords + 1, decoderEmbeddingSize], 0, 1))
	decoderEmbeddedInput = tf.nn.embedding_lookup(decoderEmbeddingsMatrix,
			preprocessedTargets)
	trainingPredictions, testPredictions = decoderRNNLayer(decoderEmbeddedInput,
			decoderEmbeddingsMatrix,
			encoderState,
			questionsNumWords,
			sequenceLength,
			rnnSize,
			numLayers,
			questionWordsToInt,
			keepProb,
			batchSize)
	return trainingPredictions, testPredictions

# ---------------------------------------
# ----- Training the SEQ2SEQ model ------
# ---------------------------------------

# Setting the Hyperparameters
epochs = 100
batchSize = 64
rnnSize = 512
numLayers = 3
encoderEmbeddingSize = 512
decodingEmbeddingSize = 512
learningRate = 0.01
learningRateDecay = 0.9
keepProbability = 0.5

# Defining a session
tf.reset_default_graph()
session = tf.InteractiveSession()

# Loading the model inputs
inputs, targets, lr, keepProb = modelInputs()

# Setting the sequence length
sequenceLength = tf.placeholder_with_default(25, None, name='sequenceLength')

# Getting the shape of the inputs tensor
inputShape = tf.shape(inputs)

# Getting the training and the test predictions
trainingPredictions, testPredictions = seqToSeqModel(tf.reverse(inputs, [-1]),
                                                     targets,
                                                     keepProb,
                                                     batchSize,
                                                     sequenceLength,
                                                     len(answerWordsToInt),
                                                     len(questionWordsToInt),
                                                     encoderEmbeddingSize,
                                                     decodingEmbeddingSize,
                                                     rnnSize,
                                                     numLayers,
                                                     questionWordsToInt)

# Setting up the Loss Error, the Optimizer and Gradient Clipping
with tf.name_scope("optimization"):
	lossError = tf.contrib.seq2seq.sequence_loss(trainingPredictions, targets,
																							tf.ones([inputShape[0], sequenceLength]))
	optimizer = tf.train.AdamOptimizer(learningRate)
	gradients = optimizer.compute_gradients(lossError)
	clippedGradients = [(tf.clip_by_value(gradTensor, -5.0, 5.0), gradVariable) for gradTensor, gradVariable in gradients if gradTensor is not None]
	optimizerGradientClipping = optimizer.apply_gradients(clippedGradients)


# Padding the sequences with the <PAD> token
def applyPadding(batchOfSequences, wordToInt):
	maxSequenceLength = max([len(sequence) for sequence in batchOfSequences])
	return [sequence + [wordToInt['<PAD>']] * (maxSequenceLength - len(sequence)) for sequence in batchOfSequences]
