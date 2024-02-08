from tmdbv3api import TMDb

from input_parser import input_parser

if __name__ == '__main__':
    tmdb = TMDb()
    tmdb.api_key = ''
    tmdb.language = 'ru'
    print('Я телеграм бот')
    while True:
        input_parser(input('Введите команду: '))
