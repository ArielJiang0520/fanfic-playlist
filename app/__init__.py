# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Configure app
socketio = SocketIO()
app = Flask(__name__, template_folder='templates')
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

UPLOAD_FOLDER = os.getcwd() + '\\app\irsystem\models'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DB
db = SQLAlchemy(app)

import sys
import pickle

DB_NAME = '/preload28k.p'
DATASET_PATH = os.getcwd() + '/dataset'
DB_PATH = DATASET_PATH + DB_NAME
sys.path.append(DATASET_PATH)
DB = pickle.load(open(DB_PATH, 'rb'))

# Import + Register Blueprints
from app.accounts import accounts as accounts
app.register_blueprint(accounts)
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404
