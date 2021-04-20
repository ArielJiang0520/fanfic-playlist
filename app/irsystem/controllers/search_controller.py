from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.search import text_search, get_rand_artists, get_rand_genres
import os
from werkzeug.utils import secure_filename
from flask import current_app, send_from_directory, Flask, request, render_template
import sys


project_name = "FanFiction Playlist Generator"
net_id = "sj784, kjh233, asd247, nk435"

#fix so changes when refreshed


ALLOWED_EXTENSIONS = {'txt'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@irsystem.route('/', methods=['GET', 'POST'])
def search():

    genres=get_rand_genres()
    artists=get_rand_artists()
    text_input = request.form.to_dict()

    if request.method == 'POST':
        if 'file' not in request.files and text_input['text'] == '':
            flash('No file or text')
            return redirect(request.url)

        if 'file' in request.files:
            file = request.files['file']
        else:
            file = ''

        # if file.filename == '' and text_input['text'] == '':
        #     flash('No selected file')
        #     return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            print(f'file id {filename} is received.', file=sys.stderr)

            text = open(
                os.path.join(current_app.config['UPLOAD_FOLDER'], filename), 'r+', encoding='utf-8'
            ).read()

            result = text_search(text)
            output_message = "Your search: " + text

            return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=result,genres=genres,artists=artists)

        if 'text' in text_input.keys():
            text = request.form.to_dict()['text']
            result = text_search(text)
            output_message = "Your search: " + text
            return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=result,genres=genres,artists=artists)

    
    return render_template('search.html', name=project_name, netid=net_id, output_message='', data='',genres=genres,artists=artists)
    
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''

@irsystem.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# @irsystem.route('/submit', methods=['POST'])
# def submit():
#     result = text_search(text)
#     output_message = "Your search: " + text
#     return render_template('search.html', name=project_name, netid=net_id, output_message=request.form['text'], data='')








# @irsystem.route('/after', methods=['GET', 'POST'])
# def after():
#     return f'''
#     <!doctype html>
#     <title>Result</title>
#     <h1>These are the top 10 songs</h1>
#     <p>{request.args.get("result")}</p>
#     '''

# @irsystem.route('/', methods=['GET', 'POST'])
# def search():
# 	query = request.args.get('search')
# 	if not query:
# 		data = []
# 		output_message = ''
# 	else:
# 		output_message = "Your search: " + query
# 		data = cosine_sim_search(query)
		
# 	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

