from . import *
from app.irsystem.models.model import text_search, get_artists, get_genres
import os
from flask import current_app, Flask, request, render_template
import sys
import requests
import json
import re

project_name = "FanFiction Playlist Generator"
net_id = "sj784, kjh233, asd247, nk435"


@irsystem.route('/', methods=['GET', 'POST'])
def search():
    text_input = request.form.to_dict() 
    link = False
    if request.method == 'POST':
        if 'text' in text_input.keys():
            text = request.form.to_dict()['text']
            if text == "" and 'link' in text_input.keys():
                text = request.form.to_dict()['link']
                link = True
            else:
                link = False
        elif 'link' in text_input.keys():
            text = request.form.to_dict()['link']
            link = True

        artist_input = request.form.to_dict()
        if 'artist_search' in artist_input.keys():
            sel_artists = request.form.to_dict()['artist_search'] # 'a,b,
            sel_artists = sel_artists.split(',') if len(sel_artists) > 0 else []
        
        genre_input = request.form.to_dict()
        if 'genre_search' in genre_input.keys():
            sel_genres = request.form.to_dict()['genre_search']
            sel_genres = sel_genres.split(',') if len(sel_genres) > 0 else []
        
        print(sel_artists, sel_genres)


        result = text_search(text, target_genres=sel_genres,
                             target_artists=sel_artists, popular=True, link=link)

        playlistid = ""
        if result['status']['code'] == '000':
            songs = []
            # fetch result here
            # data = [result['fanfic']] + [s for s in result['songs']]
            songs = ["spotify:track:" + x['id'] for x in result['songs']]
            playlistid = spotify_generator(songs)
            result['fanfic']['scores']['Sexual'] = int((
                result['fanfic']['scores']['Sexual'])*100)
            result['fanfic']['scores']['Romance'] = int((
                result['fanfic']['scores']['Romance'])*100)
            result['fanfic']['scores']['Emo'] = int((
                result['fanfic']['scores']['Emo'])*100)
            for song in result['songs']:
                song['scores']['sentiment'] = int((
                    song['scores']['sentiment'])*100)
                song['scores']['audio'] = int(
                    (song['scores']['audio'])*100)
                song['scores']['preference'] = int((
                    song['scores']['preference'])*100)
                song['scores']['lyrics'] = int(
                    (song['scores']['lyrics'])*100)

        else:
            # handle response error
            print(f"error code: {result['status']['code']}",
                    f"error message: {result['status']['msg']}")

        return render_template('output.html', name=project_name, netid=net_id,
                               genres=get_genres(), artists=get_artists(),
                               sel_genres=sel_genres, sel_artists=sel_artists, playlist=playlistid,
                               result=result)

    return render_template('search.html', name=project_name, netid=net_id, output_message='',
                           data='', genres=get_genres(), artists=get_artists())


# @irsystem.route('/spotify/', methods=['GET', 'POST'])
def song_list(result):
    list1 = []
    for tuple1 in result:
        list1.append(tuple1[1])
    return list1


def spotify_generator(song_uris):

    user_id = "gxemvx4lf4a2z1bvo33bkxul4"
    # TOKEN = requests.post("https://accounts.spotify.com/api/token", data = {
    #     "grant_type": "client_credentials"}, headers = {
    # "Authorization":"Basic MzFjZmFiZmM4ZGM4NDIzNmE2ZGU3OGM1N2ExYTg4NmI6NmViZjg4ZjA3ZjgwNGY3MTgxOGUxNGU3NmZlNDU0YzY="
    # })
    # token = json.loads(TOKEN.text)['access_token']
    token = "BQCujFE2g76NHklpEv6YLKpj7e-WTPvTIGlC4MNfzdUZoJ3omlrNY1RSao9mcTaG6G-J9BW_APOrwAugIlgGfyaQKKJFkAoE_7et1atOnnj8GTbOBBpb5onD1vZqFX39Njqc4pJhgnm2B5BxNkyOkZaZa2HFpu-dIP6RrEEkcMVOCZObVg9qiDv3DhpzbaNwNsWkEVHY0RzulKjel14pg2oLWlWmwcG6P2Vcyd-fwlhqagDo92LU3ichbiWqFN0PckQavVdNb4FpFZKUbOCLl21cBDtOZ_iCjEibvYmi"

    # for song in song_names:
    #     payload = {'q': song, 'type': 'track'}
    #     response = requests.get('https://api.spotify.com/v1/search', params=payload, headers={"Content-Type":"application/json",
    #                         "Authorization":"Bearer " + token})
    #     # response = requests.get("https://api.spotify.com/v1/search?"+song+"&type=track")
    #     results = response.json()

    #     for song in results['tracks']['items']:
    #         uris.append(song['uri'])
    # # uris.append("spotify:track:39QWEcx4aFKyx7mCQYD2Pv")
    # print(uris)
    endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    request1_body = json.dumps({
        "name": "Fanfiction Playlist",
        "description": "Most similar songs to the input.",
        "public": True
    })
    response1 = requests.post(url=endpoint_url, data=request1_body, headers={"Content-Type": "application/json",
                                                                             "Authorization": "Bearer " + token})

    # print(response1)

    if ('id' not in response1.json().keys()):
        return None

    playlist_id = response1.json()['id']
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # for s in song_uris:
    #     uris.append(s)
    # print(uris)

    request2_body = json.dumps({
        "uris": song_uris
    })

    requests.post(url=endpoint_url, data=request2_body, headers={"Content-Type": "application/json",
                                                                 "Authorization": "Bearer " + token})
    return playlist_id
