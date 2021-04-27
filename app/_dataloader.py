import scipy.sparse
import pickle
import os
import re
import random
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
from collections import Counter, defaultdict
from sklearn.metrics.pairwise import cosine_similarity

class Dataloader:
    def __init__(self):
        print('DB initialized')
        PICKLE_FOLDER = os.path.dirname(__file__) + '/pickle/'

        self.A = pickle.load(open(PICKLE_FOLDER + 'A.p', 'rb'))
        self.G = pickle.load(open(PICKLE_FOLDER + 'G.p', 'rb'))
        self.X = scipy.sparse.load_npz(PICKLE_FOLDER + 'X.npz')
        self.a_pool = pickle.load(open(PICKLE_FOLDER + 'a_pool.p', 'rb'))
        self.g_pool = pickle.load(open(PICKLE_FOLDER + 'g_pool.p', 'rb'))

        package = pickle.load(open(PICKLE_FOLDER + 'package.p', 'rb'))
        self.word_to_ix = {word: i for i, word in enumerate(package['vocab'])}
        self.V = len(self.word_to_ix)
        self.matadata = package['matadata']
        self.idf = package['idf']
        self.artists = package['artists']
        self.genres = package['genres']
        self.a_to_ix = {a: i for i, a in enumerate(package['artists'])}
        self.g_to_ix = {g: i for i, g in enumerate(package['genres'])}

    def __parse_input(self, text):
        LEM = WordNetLemmatizer()
        tokens = re.findall(r'[A-Za-z]+', text)

        tokens = [word for word, tag in nltk.pos_tag(tokens) \
            if (tag not in ['NNP', 'NNPS'])]
        
        tokens =  [LEM.lemmatize(token.lower()) for token in tokens]
        
        return tokens

    def search(self, text, t_g, t_a, k):
        tokens = self.__parse_input(text)
        q = np.zeros(shape=(1, self.V))

        term_freq = defaultdict(int, dict(Counter(tokens))) 

        for term, count in term_freq.items():
            if term in self.word_to_ix:
                q[:, self.word_to_ix[term]] += (np.log2(count) + 1) * self.idf[self.word_to_ix[term]]

        cs = cosine_similarity(self.X, q.reshape(1, -1)).flatten()
        
        doc_ids = np.argsort(-cs)[:k]
        scores = np.array([cs[doc_id] for doc_id in doc_ids])

        candidates = [self.matadata[doc_id] for doc_id in doc_ids]
        new_A = self.A[[self.artists.index(self.matadata[doc_id][0]) for doc_id in doc_ids]]

        for a in t_a:
            ix = self.a_to_ix[a]
            cs = cosine_similarity(new_A, self.A[ix].reshape(1, -1)).flatten()
            scores += cs
        
        for g in t_g:
            ix = self.g_to_ix[g]
            cs = cosine_similarity(new_A, self.G[ix].reshape(1, -1)).flatten()
            scores += cs

        return [candidates[doc_id] for doc_id in np.argsort(-scores).flatten()]
    

    def generate_pool(self, group, t):
        pool = []
        if group == 'g':
            group = self.g_pool
        else:
            group = self.a_pool

        for i in range(len(group)):
            pick = random.choice(group[i])
            while pick in pool:
                pick = random.choice(group[i])
            pool.append(pick)
            
            if len(pool) == t:
                break

        random.shuffle(pool)
        return pool


