from sklearn.preprocessing import minmax_scale
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np

from . import DB


alpha = 1.0 # base weight
beta = 0.8 # preference weight
gamma = 0.5 # audio weight

ta = 0 # base clipping threshold
tb = 0 # preference clipping threshold

f = 0.7 # popularity clipping threshold


def sentiment_score(q, threshold=ta):
    cs = cosine_similarity(q, DB.M).flatten()
    return np.where(cs < ta, 0, cs)


def pref_score(artists=[], genres=[], popular=False):
    if not artists and not genres and not popular:
        return np.ones(shape=(DB.L.shape[0], ))

    default = np.zeros(shape=(DB.A.shape[0], ))
    
    idx_a = [DB.A_TO_IX[a] for a in artists]
    idx_g = [DB.G_TO_IX[g] for g in genres]
    
    score_A = np.mean(cosine_similarity(DB.A[idx_a, :], DB.A), axis=0) if idx_a else default
    score_G = np.mean(cosine_similarity(DB.G[idx_g, :], DB.A), axis=0) if idx_g else default
    
    score_P = DB.ARTIST_POPULARITY / 100.0 if popular else default
    score_P = np.where(score_P > f, f, score_P)

    mask_P = DB.SONG_POPULARITY / 100.0 if popular else np.zeros(len(DB.MATADATA))
    mask_P = np.where(mask_P > f, f, mask_P)
    
    total_score = score_A + score_G + score_P
    
    pref = minmax_scale(np.array(
        [
            total_score[DB.A_TO_IX[DB.MATADATA[i][0]]] + mask_P[i] \
                for i in range(len(DB.MATADATA))
        ]
    ))

    return np.where(pref < tb, 0, pref)


def audio_score(q):
    return minmax_scale(np.array(
        [
            np.log2(float(1.0 - abs(DB.AUDIO_FEATURES[i][0] - q[:, -2]))) + \
            np.log2(float(1.0 - abs(DB.AUDIO_FEATURES[i][1] - q[:, -2]))) \
                for i in range(len(DB.AUDIO_FEATURES))
        ]
    ))


def lyrics_score(q_e):
    return cosine_similarity(q_e.reshape(1, -1), DB.L).flatten()


def rank(sentiment, pref, audio, lyrics, k):
    final = lyrics + alpha * sentiment + beta * pref + gamma * audio

    output = []
    for doc_id in np.argsort(-final):
        if DB.ID[doc_id] == 'nan': continue # skip missing ids

        artist, title = DB.MATADATA[doc_id]
        if artist not in [DB.MATADATA[i][0] for i in output] \
            and title not in [DB.MATADATA[i][1] for i in output]:
            output.append(doc_id)

        if len(output) >= k:
            break
    
    return output


def generate_url(i):
    artist = re.sub(r'[^A-Za-z0-9\s]', '', DB.MATADATA[i][0])
    title = re.sub(r'[^A-Za-z0-9\s]', '', DB.MATADATA[i][1])
    content = '-'.join(re.findall(r"[A-Za-z0-9]+", artist+' '+title))
    return 'https://genius.com/'+content+'-lyrics'
