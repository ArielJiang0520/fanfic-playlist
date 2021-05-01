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
    soup = BeautifulSoup(r.text)

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

    if link:
        try:
            query = scrape_link(query)
        except:
            result['status']['code'] = '001'
            result['status']['msg'] = f'link was: {query}'
            return result

    try:
        tokenized_q = tokenize_input(query)
        q = concat_proba(embed_input(tokenized_q))
    except:
        result['status']['code'] = '002'
        result['status']['msg'] = f'input was: {query}'
        return result

    ##
    pred = q.reshape(-1, )[[1, 3, 5]]
    sel_cat = np.argmax(pred)

    result['fanfic']['scores']['Sexual'] = pred[0]
    result['fanfic']['scores']['Romance'] = pred[1]
    result['fanfic']['scores']['Emo'] = pred[2]

    result['fanfic']['analysis']['sel_cat'] = cat_name[sel_cat]

    _, top_sentences = sent_analysis(sel_cat, query)

    result['fanfic']['analysis']['top_sentences'] = top_sentences

    ##
    tokenized_q_lyrics = tokenize_input(' '.join(top_sentences))

    if len(tokenized_q_lyrics) <= 0:
        result['status']['code'] = '002'
        result['status']['msg'] = f'input was: {query}'
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
        result['status']['msg'] = f'fetched result: {len(rankings)}'
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
            'genius_link': ''
        }

        song_result['id'] = DB.ID[doc_id]

        song_result['artist'] = DB.MATADATA[doc_id][0]
        song_result['title'] = DB.MATADATA[doc_id][1]

        song_result['scores']['sentiment'] = sentiment[doc_id]
        song_result['scores']['preference'] = pref[doc_id]
        song_result['scores']['audio'] = audio[doc_id]
        song_result['scores']['lyrics'] = lyrics[doc_id]

        song_result['genius_link'] = generate_url(doc_id)

        result['songs'].append(song_result)

    result['status']['code'] = '000'
    result['status']['msg'] = 'okay'

    return result


def get_rand_genres(t=8) -> [str]:
    """
    return:
        list: t number of random genres
    """
    return DB.generate_pool(group='g', t=t)

#t=8
# def get_rand_artists(t=8) -> [str]:
#     """
#     return:
#         list: t number of random artists from the database
#     """
#     return DB.generate_pool(group='a', t=t)
