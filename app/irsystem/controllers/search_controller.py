from . import *
from app.irsystem.models.model import text_search, get_rand_artists, get_rand_genres
import os
from werkzeug.utils import secure_filename
from flask import current_app, Flask, request, render_template
import sys
import requests
import json

project_name = "FanFiction Playlist Generator"
net_id = "sj784, kjh233, asd247, nk435"

ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@irsystem.route('/', methods=['GET', 'POST'])
def search():
    genre_list = get_rand_genres()
    artist_list = get_rand_artists()
    text_input = request.form.to_dict()

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']

            if not allowed_file(file.filename):
                pass

            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename))

            print(f'file id {filename} is received.', file=sys.stderr)

            text = open(
                os.path.join(current_app.config['UPLOAD_FOLDER'], filename),
                'r+', encoding='unicode_escape'
            ).read()

        if 'text' in text_input.keys():
            text = request.form.to_dict()['text']

        sel_genres = request.form.getlist('genre_box')
        print('selected genres', sel_genres)
        sel_artists = request.form.getlist('artist_box')
        print('selected artists', sel_artists)

        result = text_search(text, target_genres=sel_genres,
                             target_artists=sel_artists, popular=True, link=False)
        # print(result)
        result['fanfic']['scores']['Sexual'] = round(
            result['fanfic']['scores']['Sexual'], 2)
        result['fanfic']['scores']['Romance'] = round(
            result['fanfic']['scores']['Romance'], 2)
        result['fanfic']['scores']['Emo'] = round(
            result['fanfic']['scores']['Emo'], 2)
        for song in result['songs']:
            song['scores']['sentiment'] = round(
                song['scores']['sentiment'], 2)
            song['scores']['audio'] = round(song['scores']['audio'], 2)
            song['scores']['preference'] = round(
                song['scores']['preference'], 2)
            song['scores']['lyrics'] = round(song['scores']['lyrics'], 2)

        if result['status']['code'] == '000':
            songs = []
            # fetch result here
            data = [s['artist']+' - '+s['title'] for s in result['songs']]
            for x in result['songs']:
                songs.append("spotify:track:" + x['id'])
            playlistid = spotify_generator(songs)

        else:
            # handle response error
            data = [f"error code: {result['status']['code']}",
                    f"error message: {result['status']['msg']}"]

        return render_template('output.html', name=project_name, netid=net_id,
                               data=data, genres=genre_list, artists=artist_list,
                               sel_genres=sel_genres, sel_artists=sel_artists, playlist=playlistid,
                               result=result)

    return render_template('search.html', name=project_name, netid=net_id, output_message='',
                           data='', genres=genre_list, artists=artist_list)


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
