# -*- coding: utf-8 -*-
"""lab3-0856034.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IrAmAE9dE-g4JeqcpGFMtWc8nTKKO0ld
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from nltk.tokenize import TweetTokenizer
import nltk
import math

def get_data(filename):
  df = pd.read_json(filename, lines=True)
  print("Data size", len(df))
  corpus = [df.text[i].lower() for i in range(len(df))]
  return corpus

training_data = get_data("https://raw.githubusercontent.com/bshmueli/108-nlp/master/tweets_train.txt")
testing_data = get_data("https://raw.githubusercontent.com/bshmueli/108-nlp/master/tweets_test.txt")

"""#Part1

Find vocabulary appear 3 or more times in the train data
"""

tknzr = TweetTokenizer()
vocab = Counter()
for sentence in training_data:
  s = '<s>' + sentence + '</s>'
  tokens = tknzr.tokenize(s)
  vocab.update(tokens)
vocab = vocab.most_common()

vocabulary = [token for token, freq in vocab if freq >=3]

"""Get bigrams"""

def get_bigrams(data):
  tknzr = TweetTokenizer()
  bigrams = []
  for sentence in data:
    s = '<s>' + sentence + '</s>'
    tokens = tknzr.tokenize(s)
    for i in range(len(tokens)):
      if tokens[i] not in vocabulary:
        tokens[i] = '<UNK>'
    t = list(nltk.bigrams(tokens))
    bigrams.append(t)

  return bigrams

training_bigrams = get_bigrams(training_data)
testing_bigrams = get_bigrams(testing_data)

counts = defaultdict(lambda: defaultdict(lambda: 0))
for sentence in training_bigrams:
  for w1,w2 in sentence:
    counts[w1][w2] += 1

"""Count perplexity"""

def perplexity(data):
  perplexity = []
  for sentence in data:
    probabilities  = []
    for w1,w2 in sentence:
      probabilities.append((1 + counts[w1][w2])/(len(vocabulary)+ 1 + sum(counts[w1].values())))
    cross_entropy = (-1/len(sentence)) * sum([math.log(p, 2) for p in probabilities])
    perplexity.append(math.pow(2, cross_entropy))

  avg_perplexity = np.array(perplexity).mean()
  return avg_perplexity

test = perplexity(testing_bigrams)
train = perplexity(training_bigrams)

print("Training data:",train)
print("Testing data:",test)

"""#Part2"""

counts_back = defaultdict(lambda: defaultdict(lambda: 0))
for sentence in training_bigrams:
  for w1,w2 in sentence:
    counts_back[w2][w1] += 1

def perplexity_bi(data):
  probabilities  = []
  probabilities_back = []
  for sentence in data:
    p = []
    p_back = []
    for i in range(len(sentence[:-1])):
      w1,w2,w3 = sentence[i][0],sentence[i][1],sentence[i+1][1]
      #print(w1,w2,w3)
      p.append((1 + counts[w1][w2])/(len(vocabulary)+ 1 + sum(counts[w1].values())))
      p_back.append((1 + counts_back[w3][w2])/(len(vocabulary)+ 1 + sum(counts_back[w3].values())))
    probabilities.append(p)
    probabilities_back.append(p_back)

  avg_perplexity = []
  gamma = 0
  while gamma <=1:
    perplexity = []
    for i in range(len(data)):
      prob = np.array(probabilities[i]) * gamma +  np.array(probabilities_back[i]) * round((1-gamma),2)
      cross_entropy = (-1/prob.shape[0]) * sum([math.log(p, 2) for p in prob])
      perplexity.append(math.pow(2, cross_entropy))
    #print("{} {} {}".format(gamma,np.array(perplexity).mean()))
    avg_perplexity.append(np.array(perplexity).mean())
    gamma = round(gamma + 0.05 , 2)

  return np.argmin(avg_perplexity) , min(avg_perplexity), avg_perplexity

test_index, test_bi , test_avg_perplexity = perplexity_bi(testing_bigrams)
train_index, train_bi, train_avg_perplexity = perplexity_bi(training_bigrams)

print("training data:\ngamma = {}\nperplexity = {}\n".format(train_index*0.05,train_bi))
print("testing data:\ngamma = {}\nperplexity = {}".format(test_index*0.05,test_bi))