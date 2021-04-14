import pickle
import os
import sys

from . import DB

def cosine_sim_search(query):
    return DB.cosine_sim_rank(query)
    
