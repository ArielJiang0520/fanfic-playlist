from . import DB


def text_search(query: str, target_genres=[], target_artists=[], k=10) -> [tuple]:
    """
    param:
        query: fanfiction
        target_genres: a list of user selected genres
        target_artist: a list of user selected artists
        k: number of resulst to return
    return:
        list: songs in (artist, song_name) tuple
    """
    return DB.search(text=query, t_g=target_genres, t_a=target_artists, k=k)


def get_rand_genres(t=10) -> [str]:
    """
    return:
        list: t number of random genres
    """
    return DB.generate_genres(t)


def get_rand_artists(t=10) -> [str]:
    """
    return:
        list: t number of random artists from the database
    """
    return DB.generate_artists(t)
  