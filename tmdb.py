from tmdbv3api import TMDb, Movie, Configuration, Genre, Search
from tmdbv3api.objs import person

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


def tv_search(arg):
    pass


def mult_search(arg):
    pass


def person_search(arg):
    return Search().people(term=arg)


# person = Person()
# p = person.details(12)
#
# print(p.name)
# print(p.biography)


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
