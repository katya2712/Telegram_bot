import os

from tmdbv3api import TMDb, Movie, Configuration, Genre, Search, Discover, Person

tmdb = TMDb()
genres = []

# постер с шириной 500px
poster_w500_url = ''
profile_h632_url = ''

poster_na_url = 'https://placehold.co/500x700.png?text=N/A'
profile_na_url = 'https://placehold.co/421x632.png?text=N/A'

# id жанра мультфильмы - 16
id_mult = 16


def init():
    if os.getenv('RELEASE') is not None:
        tmdb_key = os.environ['TMDB_KEY']
    else:
        with open('secrets/tmdb.key') as file:
            tmdb_key = file.readline()
    tmdb.api_key = tmdb_key
    tmdb.language = 'ru'
    global genres
    genres = movie_genres()
    global poster_w500_url
    poster_w500_url = (info().images['secure_base_url'] +
                       info().images['poster_sizes'][-3])
    global profile_h632_url
    profile_h632_url = (info().images['secure_base_url'] +
                        info().images['profile_sizes'][-2])


def info():
    return Configuration().api_configuration()


def movie_search(arg):
    print(f'Кино с названием {arg}')


def tv_search(arg):
    pass


def person_search(arg):
    return Search().people(term=arg)


def person_details(arg):
    return Person().details(arg)


def movie_details(movie_id):
    return Movie().details(movie_id)


def similar(arg):
    pass


def recommendations(arg):
    pass


def popular():
    """Список популярных фильмов"""
    return Movie().popular()


def discover(genre_id, people_id):
    """Поиск фильмов по заданному жанру и персоне"""
    movies = Discover().discover_movies({
        'with_genres': genre_id,
        'with_people': people_id,
        # без мультфильмов
        'without_genres': id_mult,
        'sort_by': 'popularity.desc'
    })
    return movies


def movie_genres():
    """Список жанров фильмов"""
    return Genre().movie_list()
