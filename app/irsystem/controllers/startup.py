#from app.irsystem.controllers import flask_spotify_auth
from app.irsystem.controllers.flask_spotify_auth import getAuth, refreshAuth, getToken

#Add your client ID
CLIENT_ID = "31cfabfc8dc84236a6de78c57a1a886b"

#aDD YOUR CLIENT SECRET FROM SPOTIFY
CLIENT_SECRET = "6ebf88f07f804f71818e14e76fe454c6"

#Port and callback url can be changed or left to localhost:5000
PORT = "5000"
CALLBACK_URL = "http://localhost"

#Add needed scope from spotify user
SCOPE = "user-read-private user-read-email playlist-modify-public playlist-modify-private"
#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown 
TOKEN_DATA = []

def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback/".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, "{}:{}/callback/".format(CALLBACK_URL, PORT))
 
def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA
