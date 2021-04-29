from . import *
from app.irsystem.models.model import text_search, get_rand_artists, get_rand_genres
import os
from werkzeug.utils import secure_filename
from flask import current_app, Flask, request, render_template
import sys

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
        print(result)

        if result['status']['code'] == '000':
            # fetch result here
            data = [s['artist']+' - '+s['title'] for s in result['songs']]

        else:
            # handle response error
            data = [f"error code: {result['status']['code']}", f"error message: {result['status']['msg']}"]

        return render_template('output.html', name=project_name, netid=net_id,
                               data=data, genres=genre_list, artists=artist_list,
                               sel_genres=sel_genres, sel_artists=sel_artists)

    return render_template('search.html', name=project_name, netid=net_id, output_message='',
                           data='', genres=genre_list, artists=artist_list)
