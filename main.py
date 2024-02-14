import tmdb
import telegram

if __name__ == '__main__':
    print('Я телеграм бот')
    tmdb.init()
    telegram.run()
