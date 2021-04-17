import pickle
import os
import sys
from random import random


def text_search(query: str, k=10) -> [tuple]:
    """
    param:
        query: fanfiction
        k: number of resulst to return
    return:
        list: songs in (artist, song_name) tuple
    """
    return [(f'Example Artist {random.randint(1000)}', f'Example Song {random.randint(1000)}') for _ in range(k)]


def get_rand_genres(t=10) -> [str]:
    """
    return:
        list: t number of random genres
    """
    
    return [f'Genre {random.randint(1000)}' for _ in range(t)]


def get_rand_artists(t=10) -> [str]:
    """
    return:
        list: t number of random artists from the database
    """
    return [f'Artist {random.randint(1000)}' for _ in range(t)]
