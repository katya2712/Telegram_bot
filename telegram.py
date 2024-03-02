import telebot
import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import tmdb
import views.cards

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

search_type = 'movie'

with open('secrets/telegram.key') as file:
    API_TOKEN = file.readline()
bot = telebot.TeleBot(API_TOKEN)


def run():
    bot.infinity_polling()


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start', '\U0001F198Помощь'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton('/\U0001F198Помощь')
    item2 = KeyboardButton('/\U0001F3A5Фильм')
    item3 = KeyboardButton('/\U0001F3ADМультфильм')
    item4 = KeyboardButton('/\U0001F3ACСериал')

    markup.add(item1, item2, item3, item4)

    bot.send_message(message.chat.id,
                     f'''Привет,{message.from_user.first_name}!\U0001F44B
    Рады видеть тебя в нашем боте. Не будем долго болтать и приступим к выбору занятия на вечер!

    Скорее выбирай,что ты хочешь посмотреть.\U0001F447\U0001F447\U0001F447''',
                     reply_markup=markup)


@bot.message_handler(commands=['movie', '\U0001F3A5Фильм'])
def movie_selection(message):
    global search_type
    search_type = 'movie'
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Жанр',
                                 switch_inline_query_current_chat='/genre ')
    item2 = InlineKeyboardButton('Актёр',
                                 switch_inline_query_current_chat='/actor ')
    item3 = InlineKeyboardButton('Режиссёр',
                                 switch_inline_query_current_chat='/director ')

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id,
                     f'''Выберите что-нибудь:''',
                     reply_markup=markup)


@bot.message_handler(commands=['mult', '\U0001F3ADМультфильм'])
def mult_selection(message):
    global search_type
    search_type = 'mult'
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Жанр',
                                 switch_inline_query_current_chat='/genre ')
    item3 = InlineKeyboardButton('Режиссёр',
                                 switch_inline_query_current_chat='/director ')

    markup.add(item1, item3)

    bot.send_message(message.chat.id,
                     f'''Выберите что-нибудь:''',
                     reply_markup=markup)


@bot.message_handler(commands=['tv', '\U0001F3ACСериал'])
def tv_selection(message):
    global search_type
    search_type = 'tv'
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Жанр',
                                 switch_inline_query_current_chat='/genre ')
    item2 = InlineKeyboardButton('Актёр',
                                 switch_inline_query_current_chat='/actor ')
    item3 = InlineKeyboardButton('Режиссёр',
                                 switch_inline_query_current_chat='/director ')
    # item4 = InlineKeyboardButton('\U0001F3ACСериал',
    #                              switch_inline_query_current_chat='/tv')

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id,
                     f'''Выберите что-нибудь:''',
                     reply_markup=markup)


# Список популярных фильмов на сегодня
@bot.message_handler(commands=['popular', 'популярные'])
def send_popular(message):
    popular = tmdb.popular()
    # постер с шириной 500px
    poster_w500_url = (tmdb.info().images['secure_base_url'] +
                       tmdb.info().images['poster_sizes'][-3])

    for p in popular:
        markup = InlineKeyboardMarkup()
        details_button = InlineKeyboardButton("Подробнее", callback_data=f'details {p.id}')
        markup.add(details_button)
        bot.send_photo(chat_id=message.chat.id,
                       photo=poster_w500_url + p.poster_path,
                       caption=views.cards.short(
                           title=p.title,
                           overview=p.overview,
                           release_date=p.release_date[:4],
                           vote_average=p.vote_average),
                       parse_mode='HTML',
                       reply_markup=markup
                       )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    cmd = call.data.split()
    command = cmd[0]
    args = ' '.join(cmd[1:])
    if command == 'details':
        movie = tmdb.movie_details(args)
        genres = [genres['name'] for genres in movie.genres]
        bot.edit_message_caption(
            caption=views.cards.full(
                title=movie.title,
                overview=movie.overview,
                release_date=movie.release_date[:4],
                vote_average=movie.vote_average,
                length=movie.runtime,
                genres=genres),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML')


@bot.message_handler(commands=['popular', 'популярные'])
def send_popular(message):
    pass


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text[0] == '@':
        txt = message.text.split()
        if txt[0] == '@' + bot.get_me().username:
            cmd = txt[1]
            arg = ' '.join(txt[2:])
            match cmd:
                case '/genre':
                    bot.reply_to(message, f'Ищем: {search_type}, жанр: {arg}')
                case '/actor':
                    bot.reply_to(message, f'Ищем: {search_type}, актёр: {arg}')
                case '/director':
                    bot.reply_to(message, f'Ищем: {search_type}, director: {arg}')
                case _:
                    # todo использовать логер
                    print('Неизвестная команда')
    else:
        bot.reply_to(message, message.text)
