#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nltk import tokenize
import nltk
#from nltk.tokenize import RegexpTokenizer 
from nltk.util import ngrams
#from rdflib.graph import Graph
#import numpy as np
#import csv
import os.path
#import json
import sys

def MSG(s):
	sys.stderr.write(s + '\n')
	
def wait(s=""):
	print "%s \n" % s
	raw_input("Press Enter to continue...")
	
def word_ngrams(words, min=2, max=4):
    s = []
    for n in range(min, max):
        for ngram in ngrams(words, n):
            s.append(' '.join(str(i) for i in ngram))
    return s

def saveResutls(fileName, dict, th=0):
	with open(fileName, 'w') as outFile:
		for key, val in dict:
			if val >= th:
				outFile.write('{} {}\n'.format(key ,val) )
	MSG("Results are saved in a file")
	MSG(fileName)

def printResutls(dict, th=0):
	for key, val in dict:
		if val >= th:
			print '+ {}'.format(key)
		else:
			print '- {}'.format(key)
			
def saveDict(fileName, dict, th):
	with open(fileName, 'w') as outFile:
		for key, val in dict:
			if val >= th:
				outFile.write('{} {}\n'.format(key ,val) )
	MSG("File is saved.")
	MSG(fileName)
	
def loadDict(fileName, dict):
	with open(fileName, 'r') as inFile:
		text = inFile.read().decode('utf-8')
		lines = text.strip().split('\n')
		for line in lines:
			tokens = line.split(' ') 
			dict.update({' '.join(tokens[:len(tokens)-1]):tokens[len(tokens)-1]})
def buildNgram(fileName, dict, n1 = 3, n2 = 7):
	text = open(fileName).read().decode('utf-8')
	names = text.strip().split('\n')
	for name in names:
		tokens = nltk.word_tokenize(name)
		for token in tokens:
			generated_ngrams = word_ngrams(token, n1,n2)
			for ngram in generated_ngrams:
				ng = ''.join(ngram)
				if not dict.has_key(ng):
					dict.update({ng:1})
				else:
					occ=dict[ng]
					dict.update({ng:occ+1})
	print len(dict)

# to model multi word names
# replace space with _
def buildNgram2(fileName, dict, n1=3, n2=7):
	text = open(fileName).read().decode('utf-8')
	names = text.strip().split('\n')
	for name in names:
		name.replace(' ','_')
		generated_ngrams = word_ngrams(name, n1,n2)
		for ngram in generated_ngrams:
			ng = ''.join(ngram)
			if not dict.has_key(ng):
				dict.update({ng:1})
			else:
				occ=dict[ng]
				dict.update({ng:occ+1})
	print len(dict)
	
#trainFileName="data/persondata_en.nt.names.train.txt"
trainFileName="data/persondata_en.nt.names"
negativeFileName="data/corncob_lowercase.txt"

ngrams_stat = {}
ngrams_stat_sorted = {}
neg_ngrams_stat = {}
tokenizer = tokenize.RegexpTokenizer("[a-zA-Z'`éèî]+")

if len(sys.argv) > 1:
	testFileName=sys.argv[1]
	if not os.path.isfile(testFileName):
		MSG(" ## Test file does not exist." )
		MSG(testFileName)
		quit()

# read data
if os.path.isfile('data/train_ngram2.csv'):
	MSG(" ## Reading name model ...")
	loadDict('data/train_ngram2.csv', ngrams_stat)
else:
	pMSG(" ## Building name model ...")
	buildNgram2(trainFileName, ngrams_stat, 2, 7)
	ngrams_stat_sorted = sorted(ngrams_stat.iteritems(), key=lambda x:x[1], reverse=True)
	saveDict('data/train_ngram2.csv', ngrams_stat_sorted, th=10)

if os.path.isfile('data/negative_ngram2.csv'):
	MSG(" ## Loading negative ngram model ...")
	loadDict('data/negative_ngram2.csv', neg_ngrams_stat)
else:
	MSG(" ## Building negative ngram model ...")
	buildNgram2(negativeFileName, neg_ngrams_stat, 3, 7)
	neg_ngrams_stat_sorted = sorted(neg_ngrams_stat.iteritems(), key=lambda x:x[1], reverse=True)
	saveDict('data/negative_ngram2.csv', neg_ngrams_stat_sorted, th=10)
# test
MSG(" ## Reading test file ...")
text = open(testFileName).read().decode('utf-8')
names = text.strip().split('\n')
MSG(" ## Recognizing test names ...")
recognized_names = {}
for name in names:
	tokens = name.split(' ')
	tot_found=0
	tot_ngram=0
	for token in tokens:
		generated_ngrams = word_ngrams(token, 3,7)
		for ngram in generated_ngrams:
			ng = ''.join(ngram)
			if ng in ngrams_stat:
				tot_found += len(ng)
			if ng in neg_ngrams_stat:
				tot_found -= len(ng)
			tot_ngram+=len(ng)
	if(tot_ngram > 0):
		recognized_names[name] = int(100*tot_found/tot_ngram)
	else:
		recognized_names[name] = 0
	
reco_name_sorted = sorted(recognized_names.iteritems(), key=lambda x:x[1], reverse=True)

#saveResutls(testFileName+'.reco2.txt',reco_name_sorted)
printResutls(reco_name_sorted, 10)
