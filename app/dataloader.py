import pandas as pd
import pickle
import numpy as np
from itertools import chain
import os

from gensim.models import KeyedVectors
from gensim.models.phrases import Phrases

import dill
import scipy.sparse

class Dataloader:
    def __init__(self):
        print('DB initialized')

        PRELOAD_FOLDER = os.path.dirname(__file__) + '/preload'

        ### LOAD MATADATA

        DATA_FOLDER = f'{PRELOAD_FOLDER}/data'

        df = pickle.load(open(f'{DATA_FOLDER}/matadata.p', 'rb'))
        a_df = pickle.load(open(f'{DATA_FOLDER}/artist_info.p', 'rb'))

        self.MATADATA = list(zip(df['artist'].tolist(), df['title'].tolist()))
        self.ID = np.nan_to_num(df['id'].tolist(), nan='nan')

        self.SONG_POPULARITY = np.nan_to_num(df['popularity'].tolist(), nan=10)
        self.ARTIST_POPULARITY = np.nan_to_num(a_df['popularity'].tolist(), nan=10)

        self.AUDIO_FEATURES = np.nan_to_num(
            np.vstack([
                df['valence'].tolist(), 
                df['energy'].tolist(), 
                df['danceability'].tolist()
            ]),
            nan=0.5
        ).T

        self.ARTIST_POOL = a_df['artist'].tolist()
        self.A_TO_IX = {a : i for i, a in enumerate(self.ARTIST_POOL)}

        self.GENRE_POOL = sorted(list(
            set(chain.from_iterable(a_df['genre'].tolist()))
        ))
        self.G_TO_IX = {g : i for i, g in enumerate(self.GENRE_POOL)}

        self.A_TO_GENRE = {a_df.at[i, 'artist']: ', '.join(a_df.at[i, 'genre']) for i in range(len(a_df))}
        
        del a_df
        del df
        ### 


        ### LOAD W2V EMBEDDINGS

        W2V_FOLDER = f'{PRELOAD_FOLDER}/word2vec'

        self.EMBED_SIZE = 300
        self.FEATURE_SIZE = 85000

        self.EMBED_TABLE = KeyedVectors.load(f'{W2V_FOLDER}/embed85k.kv')
        assert self.EMBED_TABLE.vectors.shape == (self.FEATURE_SIZE, self.EMBED_SIZE)

        self.MODEL_VOCAB = set(self.EMBED_TABLE.key_to_index.keys())
        self.PHRASE_MODEL = Phrases.load(f'{W2V_FOLDER}/phrase_model.p')

        ###

        ### LOAD MLP

        MLP_FOLDER = f'{PRELOAD_FOLDER}/mlp'

        self.SEXUAL_CLF = pickle.load(open(f'{MLP_FOLDER}/sexual.clf', 'rb'))
        self.ROMANCE_CLF = pickle.load(open(f'{MLP_FOLDER}/romance.clf', 'rb'))
        self.EMO_CLF = pickle.load(open(f'{MLP_FOLDER}/emo.clf', 'rb'))

        ###

        ### LOAD MAT

        MAT_FOLDER = f'{PRELOAD_FOLDER}/matrix'

        self.A = np.load(f'{MAT_FOLDER}/A.npy')
        self.G = np.load(f'{MAT_FOLDER}/G.npy')

        assert len(self.ARTIST_POOL) == self.A.shape[0]
        assert len(self.GENRE_POOL) == self.G.shape[0]

        self.M = np.load(f'{MAT_FOLDER}/M_anno.npy')
        self.L = np.load(f'{MAT_FOLDER}/L.npy')

        assert self.M.shape == (len(self.MATADATA), 6)

        ### 

        print('finished loading everything!')
    