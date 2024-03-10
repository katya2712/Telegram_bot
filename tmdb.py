from tmdbv3api import TMDb, Movie, Configuration, Genre

tmdb = TMDb()
genres = []


def init():
    with open('secrets/tmdb.key') as file:
        tmdb_key = file.readline()
    tmdb.api_key = tmdb_key
    tmdb.language = 'ru'
    global genres
    genres = movie_genres()


def info():
    return Configuration().api_configuration()


def movie_search(arg):
    print(f'Кино с названием {arg}')


def mult_search(arg):
    pass


def movie_details(movie_id):
    return Movie().details(movie_id)


def similar(arg):
    pass


def recommendations(arg):
    pass


def popular():
    return Movie().popular()
    # for p in popular:
    #     print(p.id)
    #     print(p.title)
    #     print(p.overview)
    #     print(p.poster_path)


def movie_genres():
    return Genre().movie_list()
