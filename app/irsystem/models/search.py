import pickle
import os
import sys
import random as rand


def text_search(query: str, k=10) -> [tuple]:
    """
    param:
        query: fanfiction
        k: number of resulst to return
    return:
        list: songs in (artist, song_name) tuple
    """
    return [(f'Example Artist {rand.randint(0, 1000)}', f'Example Song {rand.randint(0, 1000)}') for _ in range(k)]


def get_rand_genres(t=10) -> [str]:
    """
    return:
        list: t number of random genres
    """
    
    return [f'Genre {rand.randint(0, 1000)}' for _ in range(t)]


def get_rand_artists(t=10) -> [str]:
    """
    return:
        list: t number of random artists from the database
    """
    return [f'Artist {rand.randint(0, 1000)}' for _ in range(t)]
