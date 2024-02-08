from tmdbv3api import Movie


def hlp(arg):
    print('Помощь')


def movie_search(arg):
    print(f'Кино с названием {arg}')


def mult_search(arg):
    pass


def details(arg):
    pass


def similar(arg):
    pass


def recommendations(arg):
    pass


def popular(arg):
    movie = Movie()
    popular = movie.popular()

    for p in popular:
        print(p.id)
        print(p.title)
        print(p.overview)
        print(p.poster_path)