import base64, json, requests

SPOTIFY_URL_AUTH = 'https://accounts.spotify.com/authorize/?'
SPOTIFY_URL_TOKEN = 'https://accounts.spotify.com/api/token/'
RESPONSE_TYPE = 'code'   
HEADER = 'application/x-www-form-urlencoded'
REFRESH_TOKEN = ''
    
def getAuth(client_id, redirect_uri, scope):
    data = "{}client_id={}&response_type=code&redirect_uri={}&scope={}".format(SPOTIFY_URL_AUTH, client_id, redirect_uri, scope) 
    return data

def getToken(code, client_id, client_secret, redirect_uri):
    body = {
        "grant_type": 'authorization_code',
        "code" : code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
        
     
    # encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode("utf-8"))
    # headers = {"Content-Type" : HEADER, "Authorization" : "Basic {}".format(encoded)} 

    encoded = bytes("{}:{}".format(client_id, client_secret),"utf-8")
    b64_auth_str = base64.b64encode(encoded).decode('utf-8')
    headers = {"Content-Type" : HEADER, "Authorization" : "Basic {}".format(b64_auth_str)} 

    post = requests.post(SPOTIFY_URL_TOKEN, params=body, headers=headers)
    return handleToken(json.loads(post.text))
    
def handleToken(response):
    try:
        auth_head = {"Authorization": "Bearer {}".format(response["access_token"])}
        global GLOBAL_ACCESS_TOKEN
        GLOBAL_ACCESS_TOKEN = response['access_token']
        global GLOBAL_SCOPE
        GLOBAL_SCOPE = response['scope']
        global GLOBAL_EXPIRES
        GLOBAL_EXPIRES = response['expires_in']
        global GLOBAL_REFRESH
        GLOBAL_REFRESH = response['refresh_token']
    except:
        #global GLOBAL_ACCESS_TOKEN
        response["access_token"] = GLOBAL_ACCESS_TOKEN
        response["scope"] = GLOBAL_SCOPE
        response["refresh_token"] = GLOBAL_REFRESH
        response['expires_in'] = GLOBAL_EXPIRES
        auth_head = {"Authorization": "Bearer {}".format(response["access_token"])}
    REFRESH_TOKEN = response["refresh_token"]
    return [response["access_token"], auth_head, response["scope"], response["expires_in"]]
        

def refreshAuth():
    body = {
        "grant_type" : "refresh_token",
        "refresh_token" : REFRESH_TOKEN
    }

    post_refresh = requests.post(SPOTIFY_URL_TOKEN, data=body, headers=HEADER)
    p_back = json.dumps(post_refresh.text)
    
    return handleToken(p_back)
