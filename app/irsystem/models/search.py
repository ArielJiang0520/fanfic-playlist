import pickle
import os
import sys

DB_NAME = '/preload28k.p'
DATASET_PATH = os.getcwd() + '/dataset'
DB_PATH = DATASET_PATH + DB_NAME

sys.path.append(DATASET_PATH)

DB = pickle.load(open(DB_PATH, 'rb'))

def cosine_sim_search(query):
    
    #db = LyricsDB(pickle.load(open('genius28k.p', 'rb')))
    return DB.cosine_sim_rank(query)
    
