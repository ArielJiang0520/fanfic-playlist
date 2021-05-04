from . import DB
from .input_handler import tokenize_input, embed_input, concat_proba, sent_analysis
from .ranking_sys import sentiment_score, pref_score, audio_score, lyrics_score, rank, generate_url

from bs4 import BeautifulSoup
import requests
import numpy as np

cat_name = {0: 'Sexual', 1: 'Romance', 2: 'Emo'}


def scrape_link(url: str):
    headers = {'user-agent': 'bot (sj784@cornell.edu)'}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, features="lxml")

    output = ''
    if soup.find_all('div', class_="userstuff module", role='article'):
        for chapter in soup.find_all('div', class_="userstuff module", role='article'):
            output += chapter.get_text()+'\n'

    elif soup.find('div', class_='userstuff'):
        output += soup.find('div', class_='userstuff').get_text()

    else:
        # print(f'can not find text for {url}')
        raise AssertionError

    return output


def text_search(query: str, target_genres=[], target_artists=[],
                popular=True, k=10, link=False) -> [dict]:
    """
    param:
        query: fanfiction
        target_genres: a list of user selected genres
        target_artist: a list of user selected artists
        popular: bool
        k: number of resulst to return
    return:
        see below
    """

    result = {
        'songs': [],  # list of k song_results
        'fanfic': {
            'scores': {
                'Sexual': 0.0,
                'Romance': 0.0,
                'Emo': 0.0
            },
            'analysis':
            {
                'sel_cat': '',  # [Romance | Emo | Sexual]
                'top_sentences': []  # 30 sentences
            }
        },
        'status': {
            'code': '',
            'msg': ''
        }
    }

    if target_artists or target_genres:
        if any([a not in DB.ARTIST_POOL for a in target_artists]) or \
            any([g not in DB.GENRE_POOL for g in target_genres]):
            result['status']['code'] = '004'
            result['status']['msg'] = f'The artists you selected ("{target_artists}") or the genres you selected ("{target_genres}") are not in the database.'
            return result

    if link:
        try:
            query = scrape_link(query)
        except:
            result['status']['code'] = '001'
            result['status']['msg'] = f'The link you entered, "{query}", is invalid.'
            return result

    try:
        tokenized_q = tokenize_input(query)
        q = concat_proba(embed_input(tokenized_q))
    except:
        result['status']['code'] = '002'
        result['status']['msg'] = f'The input you entered, "{query}", is invalid. Possible reason is input length too short.'
        return result

    ##
    pred = q.reshape(-1, )[[1, 3, 5]]
    sel_cat = np.argmax(pred)

    result['fanfic']['scores']['Sexual'] = int(pred[0] * 100)
    result['fanfic']['scores']['Romance'] = int(pred[1] * 100)
    result['fanfic']['scores']['Emo'] = int(pred[2] * 100)

    result['fanfic']['analysis']['sel_cat'] = cat_name[sel_cat]

    _, top_sentences = sent_analysis(sel_cat, query)

    result['fanfic']['analysis']['top_sentences'] = top_sentences

    ##
    tokenized_q_lyrics = tokenize_input(' '.join(top_sentences))

    if len(tokenized_q_lyrics) <= 0:
        result['status']['code'] = '002'
        result['status']['msg'] = f'The input you entered, "{query}", is invalid. Possible reason is input length too short.'
        return result

    q_e = embed_input(tokenized_q_lyrics)

    ##
    sentiment = sentiment_score(q)
    pref = pref_score(target_artists, target_genres, popular)
    audio = audio_score(q)
    lyrics = lyrics_score(q_e)
    
    ##
    rankings = rank(sentiment, pref, audio, lyrics, k)

    if len(rankings) != k:
        result['status']['code'] = '003'
        result['status']['msg'] = f'There are not enough results in our database that matches your query. Please try again with a different query.'
        return result

    for doc_id in rankings:
        song_result = {
            'id': '',
            'artist': '',
            'title': '',
            'scores': {
                'sentiment': 0.0,
                'audio': 0.0,
                'preference': 0.0,
                'lyrics': 0.0
            },
            'artist_genre': '',
            'artist_popularity': '',
            'song_popularity': 0,
            'genius_link': ''
        }

        song_result['id'] = DB.ID[doc_id]

        song_result['artist'] = DB.MATADATA[doc_id][0]
        song_result['title'] = DB.MATADATA[doc_id][1]

        song_result['scores']['sentiment'] = int(sentiment[doc_id] * 100)
        song_result['scores']['preference'] = int(pref[doc_id] * 100)
        song_result['scores']['audio'] = int(audio[doc_id] * 100)
        song_result['scores']['lyrics'] = int(lyrics[doc_id] * 100)
        
        song_result['artist_genre'] = DB.A_TO_GENRE[DB.MATADATA[doc_id][0]]
        song_result['artist_popularity'] = int(DB.ARTIST_POPULARITY[DB.A_TO_IX[DB.MATADATA[doc_id][0]]])
        song_result['song_popularity'] = int(DB.SONG_POPULARITY[doc_id])
        song_result['genius_link'] = generate_url(doc_id)

        result['songs'].append(song_result)

    result['status']['code'] = '000'
    result['status']['msg'] = 'okay'

    return result


def get_genres() -> [str]:
    """
    return:
        all genres
    """
    return DB.GENRE_POOL

def get_artists() -> [str]:
    """
    return:
        all artists
    """
    return DB.ARTIST_POOL
