import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import *

from nltk import word_tokenize
from nltk.corpus import words, stopwords

from collections import defaultdict, Counter

DICTIONARY = set(words.words())
STOPWORDS = set(stopwords.words('english'))

class LyricsDB:
    def __init__(self, df):
        self.N = len(df)
        self.corpus = df['lyrics'].tolist()
        self.matadata = list(zip(df['artist'].tolist(), df['title'].tolist()))
    
    def __len__(self):
        return self.N
    
    def __getitem__(self, doc_id: int):
        assert type(doc_id) == int
        return self.matadata[doc_id]
    
    def __custom(self, text):
        return [token for token in word_tokenize(text) if token in DICTIONARY and len(token) > 1]
    
    def fit(self, preload=False):
        vectorizer = TfidfVectorizer(
            tokenizer=self.__custom,
            strip_accents='ascii',
            stop_words='english',
            token_pattern=None
        )
        vectorizer.fit(self.corpus)

        self.X = vectorizer.transform(self.corpus)
        
        self.vocab = vectorizer.get_feature_names()
        self.V = len(self.vocab)
        self.word_to_ix = vectorizer.vocabulary_
        
        self.idf = vectorizer.idf_
        self.doc_terms = vectorizer.inverse_transform(self.X)

    def get_lyrics_from_id(self, doc_id):
        return self.doc_terms[doc_id]
    
    def search_artist(self, artist):
        return [(i, line[0], line[1]) for i, line in enumerate(self.matadata) if line[0].lower() == artist.lower()]
    
    def search_song(self, song):
        return [(i, line[0], line[1]) for i, line in enumerate(self.matadata) if line[1].lower() == song.lower()] 
    
    def cosine_sim_rank(self, text: str, k=10):
        tokens = [token for token in word_tokenize(text.lower())]
        # no handle unknown words
        term_freq = defaultdict(int, dict(Counter(tokens))) 
        
        q = dok_matrix((1, self.V), dtype=float)
        for term, count in term_freq.items():
            if term in self.word_to_ix:
                q[:, self.word_to_ix[term]] = count * self.idf[self.word_to_ix[term]]
        
        cs = cosine_similarity(self.X, q.reshape(1, -1), dense_output=True).flatten()
        
        output = []
        for doc_id in np.argsort(-cs)[:k]:
            output.append((int(doc_id), self[int(doc_id)], cs[doc_id]))
        
        return output


