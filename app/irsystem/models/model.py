from . import DB
from .input_handler import tokenize_input, embed_input, concat_proba
from .ranking_sys import base_score, pref_score, audio_score

import numpy as np

def text_search(query: str, target_genres=[], target_artists=[], k=10) -> [tuple]:
    """
    param:
        query: fanfiction
        target_genres: a list of user selected genres
        target_artist: a list of user selected artists
        k: number of resulst to return
    return:
        list: songs in (artist, song_name) tuple
    """
    tokenized_q = tokenize_input(query)
    q = concat_proba(embed_input(tokenized_q))

    # classifier score
    base = base_score(q)
    alpha = 1.0

    # user preference score
    pref = pref_score(artists=target_artists, genres=target_genres, popular=True)
    beta = 0.5

    # audio feature score
    audio = audio_score(q)
    gamma = 0.5

    assert base.shape[0] == pref.shape[0] == audio.shape[0]

    final = alpha * base + beta * pref + gamma * audio

    return [(DB.MATADATA[doc_id], round(final[doc_id],4)) for doc_id in np.argsort(-final)[:10]]
    

def get_rand_genres(t=8) -> [str]:
    """
    return:
        list: t number of random genres
    """
    return DB.generate_pool(group='g', t=t)

#t=8
def get_rand_artists(t=3000) -> [str]:
    """
    return:
        list: t number of random artists from the database
    """
    return DB.generate_pool(group='a', t=t)
  