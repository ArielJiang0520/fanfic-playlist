from . import *
from app.irsystem.models.model import text_search, get_artists, get_genres
import os
from flask import current_app, Flask, request, render_template, redirect
import sys
import requests
import json
import re
from app.irsystem.controllers import startup

project_name = "FanFiction Playlist Generator"
net_id = "sj784, kjh233, asd247, nk435"


@irsystem.route('/', methods=['GET', 'POST'])
def search():
    text_input = request.form.to_dict()
    link = False
    popular = False
    if request.method == 'POST':
        if text_input['text-or-link'] == "link":
            link = True
            text = text_input['text']
            if text == "" and 'link' in text_input:  # this is for easy toggling between old and new ui
                text = text_input['link']
        if text_input['text-or-link'] == "text":
            link = False
            text = text_input['text']
        if 'popular' in text_input.keys() and text_input["popular"] == "Popular":
            popular = True

        artist_input = request.form.to_dict()
        if 'artist_search' in artist_input.keys():
            sel_artists = request.form.to_dict()['artist_search']  # 'a,b,
            sel_artists = sel_artists.split(
                ',') if len(sel_artists) > 0 else []

        genre_input = request.form.to_dict()
        if 'genre_search' in genre_input.keys():
            sel_genres = request.form.to_dict()['genre_search']
            sel_genres = sel_genres.split(',') if len(sel_genres) > 0 else []

        # print(sel_artists, sel_genres)

        result = text_search(text, target_genres=sel_genres,
                             target_artists=sel_artists, popular=popular, link=link)

        if not result['status']['code'] == '000':
            # handle response error
            print(f"error code: {result['status']['code']}",
                  f"error message: {result['status']['msg']}")
            return render_template('404.html', code=result['status']['code'], message=result['status']['msg'])

        global results_list
        results_list = [project_name, net_id, get_genres(), get_artists(
        ), sel_genres, sel_artists, result, startup.getUser()]
        return render_template('output2.html', name=project_name, netid=net_id,
                               genres=get_genres(), artists=get_artists(),
                               sel_genres=sel_genres, sel_artists=sel_artists, popular=popular,
                               result=result, song_shown=0, spotify_auth_url="http://localhost:5000/spotify/")

    return render_template('search2.html', name=project_name, netid=net_id, output_message='',
                           data='', genres=get_genres(), artists=get_artists())


@irsystem.route('/v2', methods=['GET', 'POST'])
def searchv2():
    text_input = request.form.to_dict()
    link = False
    popular = False
    if request.method == 'POST':
        if text_input['text-or-link'] == "link":
            link = True
            text = text_input['text']
            if text == "" and 'link' in text_input:  # this is for easy toggling between old and new ui
                text = text_input['link']
        if text_input['text-or-link'] == "text":
            link = False
            text = text_input['text']
        if 'popular' in text_input.keys() and text_input["popular"] == "Popular":
            popular = True

        artist_input = request.form.to_dict()
        if 'artist_search' in artist_input.keys():
            sel_artists = request.form.to_dict()['artist_search']  # 'a,b,
            sel_artists = sel_artists.split(
                ',') if len(sel_artists) > 0 else []

        genre_input = request.form.to_dict()
        if 'genre_search' in genre_input.keys():
            sel_genres = request.form.to_dict()['genre_search']
            sel_genres = sel_genres.split(',') if len(sel_genres) > 0 else []

        # print(sel_artists, sel_genres)

        result = text_search(text, target_genres=sel_genres,
                             target_artists=sel_artists, popular=popular, link=link)

        if not result['status']['code'] == '000':
            # handle response error
            print(f"error code: {result['status']['code']}",
                  f"error message: {result['status']['msg']}")
            return render_template('404.html', code=result['status']['code'], message=result['status']['msg'])

        global results_list
        results_list = [project_name, net_id, get_genres(), get_artists(
        ), sel_genres, sel_artists, result, startup.getUser()]
        return render_template('output.html', name=project_name, netid=net_id,
                               genres=get_genres(), artists=get_artists(),
                               sel_genres=sel_genres, sel_artists=sel_artists, popular=popular,
                               result=result, song_shown=0, spotify_auth_url="http://localhost:5000/spotify/")

    return render_template('search.html', name=project_name, netid=net_id, output_message='',
                           data='', genres=get_genres(), artists=get_artists())


@irsystem.route('/spotify/')
def login():
    response = startup.getUser()
    return redirect(response)


@irsystem.route('/callback/')
def callback():
    startup.getUserToken(request.args['code'])
    # print(startup.getAccessToken())
    global results_list
    playlistid = ""
    if results_list[6]['status']['code'] == '000':
        songs = []
        # fetch result here
        songs = ["spotify:track:" + x['id'] for x in results_list[6]['songs']]
        playlistid = spotify_generator(songs)

    return render_template('output2.html', name=results_list[0], netid=results_list[1],
                           genres=results_list[2], artists=results_list[3],
                           sel_genres=results_list[4], sel_artists=results_list[5], playlist=playlistid,
                           result=results_list[6], spotify_auth_url=results_list[7], song_shown=0, clicked=True)


# @irsystem.route('/spotify/', methods=['GET', 'POST'])
def song_list(result):
    list1 = []
    for tuple1 in result:
        list1.append(tuple1[1])
    return list1


def spotify_generator(song_uris):
    token = startup.getAccessToken()[0]

    endpoint_url = f"https://api.spotify.com/v1/me"
    response = requests.get(url=endpoint_url, headers={
                            "Authorization": "Bearer " + token})
    results = response.json()
    user_id = results['id']

    #user_id = "gxemvx4lf4a2z1bvo33bkxul4"
    # TOKEN = requests.post("https://accounts.spotify.com/api/token", data = {
    #     "grant_type": "client_credentials"}, headers = {
    # "Authorization":"Basic MzFjZmFiZmM4ZGM4NDIzNmE2ZGU3OGM1N2ExYTg4NmI6NmViZjg4ZjA3ZjgwNGY3MTgxOGUxNGU3NmZlNDU0YzY="
    # })
    # token = json.loads(TOKEN.text)['access_token']
    #token = "BQCujFE2g76NHklpEv6YLKpj7e-WTPvTIGlC4MNfzdUZoJ3omlrNY1RSao9mcTaG6G-J9BW_APOrwAugIlgGfyaQKKJFkAoE_7et1atOnnj8GTbOBBpb5onD1vZqFX39Njqc4pJhgnm2B5BxNkyOkZaZa2HFpu-dIP6RrEEkcMVOCZObVg9qiDv3DhpzbaNwNsWkEVHY0RzulKjel14pg2oLWlWmwcG6P2Vcyd-fwlhqagDo92LU3ichbiWqFN0PckQavVdNb4FpFZKUbOCLl21cBDtOZ_iCjEibvYmi"

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
