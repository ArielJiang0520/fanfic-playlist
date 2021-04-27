from sklearn.preprocessing import minmax_scale
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np

from . import DB

def base_score(q, threshold=0.98):
    cs = cosine_similarity(q, DB.M).flatten()
    return np.where(cs < threshold, 0, cs)


def pref_score(artists=[], genres=[], popular=False):
    default = np.zeros(shape=(DB.A.shape[0], ))
    
    idx_a = [DB.A_TO_IX[a] for a in artists]
    idx_g = [DB.G_TO_IX[g] for g in genres]
    
    score_A = np.mean(cosine_similarity(DB.A[idx_a, :], DB.A), axis=0) if idx_a else default
    score_G = np.mean(cosine_similarity(DB.G[idx_g, :], DB.A), axis=0) if idx_g else default
    
    score_P = DB.ARTIST_POPULARITY / 100.0 if popular else default
    mask_P = DB.SONG_POPULARITY / 100.0 if popular else np.zeros(len(DB.MATADATA))
    
    total_score = score_A + score_G + score_P
    
    return minmax_scale(np.array(
        [
            total_score[DB.A_TO_IX[DB.MATADATA[i][0]]] + mask_P[i] \
                for i in range(len(DB.MATADATA))
        ]
    ))


def audio_score(q):
    return minmax_scale(np.array(
        [
            float(1.0 - abs(DB.AUDIO_FEATURES[i][0] - q[:, -2])) + \
            float(1.0 - abs(DB.AUDIO_FEATURES[i][1] - q[:, -2])) \
                for i in range(len(DB.AUDIO_FEATURES))
        ]
    ))