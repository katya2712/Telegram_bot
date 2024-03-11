import telebot
import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telebot.util import quick_markup

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
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton('/\U0001F198Помощь')
    item2 = KeyboardButton('/\U0001F3A5Фильм')
    item3 = KeyboardButton('/\U0001F3ADМультфильм')
    item4 = KeyboardButton('/\U0001F3ACСериал')
    item5 = KeyboardButton('/\U0001F51DТоп_фильмов')

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(message.chat.id,
                     f'''Привет,{message.from_user.first_name}!\U0001F44B
Рады видеть тебя в нашем боте. Не будем долго болтать и приступим к выбору занятия на вечер!

Скорее выбирай,что ты хочешь посмотреть.\U0001F447\U0001F447\U0001F447''',
                     reply_markup=markup)


@bot.message_handler(commands=['help', '\U0001F198Помощь'])
def movie_selection(message):
    bot.send_message(message.chat.id,
                     f'''1️⃣Чтобы бот начал работать, нажмите кнопку: <b>start</b>.
2️⃣Выберете, что вы хотите посмотреть и в зависмости от выбора нажмите кнопку: <b>фильм</b>, <b>мультфильм</b> или <b>сериал</b>.
3️⃣После того как вы выбрали, что вы хотите посмотреть, вам будут предложены ещё три кнопки: жанр, актёры и режиссёр. Нажмите на любую из них и напишите любимый жанр, актёра или режиссёра. Затем бот предложит несколько фильмов, мультфильмов или сериалов, выберете один из них, запаситесь вкусняшками и наслаждайтесь просмотром!\U0001F497
4️⃣Если вы хотите посмотреть просто какой-то популярный фильм, нажмите кнопку: топ фильмов.''', parse_mode='HTML')


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
                     f'''Выберете что-нибудь:''',
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
                     f'''Выберете что-нибудь:''',
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
                     f'''Выберете что-нибудь:''',
                     reply_markup=markup)


# Список популярных фильмов на сегодня
@bot.message_handler(commands=['popular', '\U0001F51DТоп_фильмов'])
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


@bot.message_handler(commands=['movie_genres', 'жанры_фильмов'])
def send_genres(message):
    buttons = {}
    for genre in tmdb.genres:
        buttons[genre.name] = {'callback_data': f'genre_id {genre.id}'}
    markup = quick_markup(buttons, row_width=3)
    bot.send_message(chat_id=message.chat.id,
                     text=f'Выберите жанр',
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
    elif command == 'genre_id':
        bot.answer_callback_query(callback_query_id=call.id,
                                  text=f'id жанра - {args}')
        # bot.send_message(chat_id=call.message.chat.id,
        #                  text=f'id жанра - {args}')


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
                    # использовать логер
                    print('Неизвестная команда')
    else:
        bot.reply_to(message, message.text)
