from . import DB
from itertools import chain
from collections import Counter, defaultdict
import numpy as np
import re

import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 

LEM = WordNetLemmatizer()
STOPWORDS = set(stopwords.words('english'))

PATTERN = r'''(?x)          # set flag to allow verbose regexps
    (?:[a-z]\.)+        # abbreviations, e.g. U.S.A.
    | \w+(?:-\w+)*        # words with optional internal hyphens
'''

def tokenize_corpus(corpus):
    output = []
    for doc in corpus:
        sentences = sent_tokenize(doc) 
        for sent in sentences:
            output.append(nltk.regexp_tokenize(sent.lower(), PATTERN))
    return output


def convert_phrases(tokenized_sent, phrase_model=DB.PHRASE_MODEL):
    output = []
    for sent in tokenized_sent:
        if sent == []:
            output.append([])
        else:
            tokens, _ = zip(*phrase_model.analyze_sentence(sent))
            output.append(list(tokens))
    return output


def convert_unk(tokenized_sent, vocab=DB.MODEL_VOCAB):
    output = []
    for sent in tokenized_sent:
        tokens = [tok if tok in vocab else '<UNK>' for tok in sent]
        output.append(tokens)
    return output


def tokenize_input(text):
    tokenized_sent = convert_phrases(tokenize_corpus([text]))
    tokenized_sent = convert_unk(tokenized_sent)
    return list(chain.from_iterable(tokenized_sent))


def embed_input(tokenized_query):
    vec = np.zeros(shape=(len(tokenized_query), DB.EMBED_SIZE))

    for j, term in enumerate(tokenized_query):
        vec[j] = DB.EMBED_TABLE[term]
        
    return np.mean(vec, axis=0).reshape(1, -1)
    

def concat_proba(input_):
    input_ = input_.reshape(1, -1)
    vec = []
    for model in [DB.SEXUAL_CLF, DB.ROMANCE_CLF, DB.EMO_CLF]:
        vec.append(model.predict_proba(input_))
    
    return np.concatenate(vec, axis=1).reshape(1, -1)


def sent_analysis(cat, text):
    cat1, cat2 = {}, {}
    sentences = sent_tokenize(text)
    for sent in sentences:
        tokenized_s = tokenize_input(sent)
        if len(tokenized_s) > 3:
            s = concat_proba(embed_input(tokenized_s))
            cat1[sent] = s[:, cat*2]
            cat2[sent] = s[:, cat*2+1]
    
    return sorted(cat1, key=lambda x:-cat1[x])[:20], \
        sorted(cat2, key=lambda x:-cat2[x])[:20]