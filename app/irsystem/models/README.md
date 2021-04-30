## usage

`text_search` 

function input:

```

query: text or link
target_genres: a list of user selected genres
target_artist: a list of user selected artists
popular: bool
k: number of resulst to return  
link: if the query is a link or not

```

response format (refer to error code):

```python
{
    'fanfic': {
        'scores': {
                'sexual': 0.0,
                'romance': 0.0,
                'emo': 0.0
            },
        'analysis': {
            'sel_cat': '', # [romance | emo | sexual] 
            'top_sentences': [] # 30 sentences (truncate if you want)
        }
    },
    'songs': [

        {
            'id': '',
            'artist':  '',
            'title': '',
            'scores': {
                'sentiment': 0.0, # all the scores need to x100 to make to percentage
                'audio': 0.0,
                'preference': 0.0,
                'lyrics': 0.0
            },
            'genius_link': ''
        },

        {
            'id': ''
            # ....
        }

    ],
    'status': {
        'code': '', # error code
        'msg': '' # error message
}

error_code = {
    '000': 'okay',
    '001': 'link error',
    '002': 'input error',
    '003': 'not enough results error'
}
```

`get_rand_artists` response format:

```python

['Justin Bieber', '...', '...'] # this is fixed right now, will always return top 10 genres

```


`get_rand_artists` response format:

```python

['pop', 'hip hop', '...', '..'] # this is fixed right now, will always return top 10 artists

```

