import os

import telebot
import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    InputMediaPhoto
from telebot.util import quick_markup

import tmdb
import views.cards
import config

if os.getenv('RELEASE') is not None:
    API_TOKEN = os.environ['TELEGRAM_KEY']
else:
    with open('secrets/telegram.key') as file:
        API_TOKEN = file.readline()

bot = telebot.TeleBot(API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# ### Структура хранения состояния поиска для каждого пользователя
# {
# chat_id: {
# 	'discover': [],
# 	'genre_id': '',
# 	'current_discover_id': 0
# 	}
users = {}

prev_button = InlineKeyboardButton("prev", callback_data=f'prev')
next_button = InlineKeyboardButton("next", callback_data=f'next')


def run():
    bot.infinity_polling()


# ----- Обработчики команд -----

# Обработчик '/start'
@bot.message_handler(commands=['start', 'старт'])
def start(message):
    chat_id = message.chat.id
    global users
    users[chat_id] = {}
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton('\U0001F3A5Фильм')
    item2 = KeyboardButton('\U0001F3ACСериал')
    item3 = KeyboardButton('\U0001F51DТоп фильмов')
    item4 = KeyboardButton('\U0001F198Помощь')
    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id,
                     f'''Привет,{message.from_user.first_name}!\U0001F44B
Рады видеть тебя в нашем боте. Не будем долго болтать и приступим к выбору занятия на вечер!

Скорее выбирай,что ты хочешь посмотреть.\U0001F447\U0001F447\U0001F447''',
                     reply_markup=markup)


# Обработчик '/help'
@bot.message_handler(commands=['help', 'помощь'])
def send_help_handler(message):
    send_help(message.chat.id)


# Вызов помощи из клавиатуры
@bot.message_handler(func=lambda message: message.text == '\U0001F198Помощь')
def help_handler(message):
    send_help(message.chat.id)


@bot.message_handler(commands=['version', 'версия'])
def send_version_handler(message):
    chat_id = message.chat.id
    version = config.version
    bot.send_message(chat_id=chat_id,
                     text=version)


@bot.message_handler(commands=['popular', 'популярные'])
def send_popular(chat_id):
    """Список популярных фильмов на сегодня"""
    popular = tmdb.popular()

    # TODO Выводить список в одном сообщении по аналогии с результатами поиска
    for p in popular:
        markup = InlineKeyboardMarkup()
        details_button = InlineKeyboardButton("Подробнее", callback_data=f'details {p.id}')
        markup.add(details_button)
        bot.send_photo(chat_id=chat_id,
                       photo=tmdb.poster_w500_url + p.poster_path,
                       caption=views.cards.movie_short(
                           title=p.title,
                           release_date=p.release_date[:4],
                           vote_average=p.vote_average),
                       parse_mode='HTML',
                       reply_markup=markup
                       )


# Поиск фильмов
@bot.message_handler(func=lambda message: message.text == '\U0001F3A5Фильм')
def send_genres_handler(message):
    """Отправляет пользователю список доступных жанров фильмов"""
    chat_id = message.chat.id
    # создаем словарь для каждого пользователя
    users[chat_id] = {}
    users[chat_id]['discover'] = []
    users[chat_id]['genre_id'] = ''
    users[chat_id]['current_discover_id'] = 0

    buttons = {}
    for genre in tmdb.genres:
        buttons[genre.name] = {'callback_data': f'genre_id {genre.id} {genre.name}'}
    markup = quick_markup(buttons, row_width=3)
    bot.send_message(chat_id=chat_id,
                     text='<b>Выберите жанр:</b>',
                     parse_mode='HTML',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '\U0001F3ACСериал')
def send_tv_handler(message):
    """Отправляет пользователю список доступных жанров сериалов"""
    chat_id = message.chat.id
    # создаем словарь для каждого пользователя
    users[chat_id] = {}
    users[chat_id]['discover'] = []
    users[chat_id]['genre_id'] = ''
    users[chat_id]['current_discover_id'] = 0

    buttons = {}
    for genre in tmdb.genres:
        buttons[genre.name] = {'callback_data': f'genre_id {genre.id} {genre.name}'}
    markup = quick_markup(buttons, row_width=3)
    bot.send_message(chat_id=chat_id,
                     text=f'<b>Выберите жанр:</b>',
                     parse_mode='HTML',
                     reply_markup=markup)


# Список популярных фильмов
@bot.message_handler(func=lambda message: message.text == '\U0001F51DТоп фильмов')
def send_popular_handler(message):
    send_popular(message.chat.id)


@bot.message_handler(func=lambda message: users[message.chat.id]['genre_id'] != '')
def send_person_handler(message):
    # Если выбран жанр, любое текстовое сообщение трактуем как поиск персоны (актера или режиссёра)
    # Выполняется если не обнаружена другая команда
    persons = tmdb.person_search(message.text)
    if persons.total_results > 0:
        for person in persons:
            if person.profile_path is not None and person.profile_path != '':
                person_profile_picture = str(tmdb.profile_h632_url + person.profile_path)
            else:
                person_profile_picture = tmdb.profile_na_url
            details = tmdb.person_details(person.id)
            markup = InlineKeyboardMarkup()
            select_button = InlineKeyboardButton("Выбрать", callback_data=f'select_person {person.id}')
            markup.add(select_button)
            films = ', '.join([film.title for film in person.known_for])
            text = views.cards.person_short(name=person.name,
                                            date_of_birth=details.birthday,
                                            films=films
                                            )
            bot.send_photo(chat_id=message.chat.id,
                           photo=person_profile_picture,
                           caption=text,
                           parse_mode='HTML',
                           reply_markup=markup
                           )
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f'По запросу "{message.text}" ничего не найдено, введите заново имя и фамилию актёра или режиссёра.')


# Обработчик всех других неизвестных текстовых команд
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    # TODO доделать обработчик неизвестных команд (или убрать)
    text = f'Неизвестная команда. "{message.text}"'
    bot.reply_to(message=message, text=text)


# ----- Обработчики колбэков из кнопок -----

# TODO воспользоваться возможностями лямбда функции декоратора

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id = call.message.chat.id
    cmd = call.data.split()
    command = cmd[0]
    args = ' '.join(cmd[1:])
    if command == 'details':
        movie = tmdb.movie_details(args)
        genres = [genres['name'] for genres in movie.genres]
        bot.edit_message_caption(
            caption=views.cards.movie_full(
                title=movie.title,
                overview=movie.overview,
                release_date=movie.release_date[:4],
                vote_average=movie.vote_average,
                length=movie.runtime,
                genres=genres),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML')
    if command == 'details_from_discover':
        movie = tmdb.movie_details(args)
        movie_count = len(users[chat_id]['discover'])
        genres = [genres['name'] for genres in movie.genres]
        markup = InlineKeyboardMarkup()

        # добавляем кнопку "предыдущий", если фильм не первый
        if users[chat_id]['current_discover_id'] > 0:
            markup.add(prev_button)

        # добавляем кнопку "следующий", если фильм не последний
        if users[chat_id]['current_discover_id'] < movie_count - 1:
            markup.add(next_button)

        bot.edit_message_caption(
            caption=views.cards.movie_full(
                title=movie.title,
                overview=movie.overview,
                release_date=movie.release_date[:4],
                vote_average=movie.vote_average,
                length=movie.runtime,
                genres=genres),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup)

    elif command == 'genre_id':
        args = args.split()
        users[chat_id]['genre_id'] = args[0]
        # variables.genre_id = args[0]
        genre_name = ' '.join(args[1:])
        bot.answer_callback_query(callback_query_id=call.id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'Выбран жанр {genre_name}.\n Напишите имя актёра или режиссёра.')

    elif command == 'select_person':
        users[chat_id]['discover'] = tmdb.discover(genre_id=users[chat_id]['genre_id'], people_id=args)
        bot.answer_callback_query(callback_query_id=call.id)
        if users[chat_id]['discover']['total_results'] > 0:
            send_first_movie(call=call)
        else:
            bot.send_message(chat_id=chat_id,
                             text='По вашему запросу ничего не найдено. Пожалуйста, повторите поиск.')

    elif command == 'next':
        users[chat_id]['current_discover_id'] += 1
        # bot.answer_callback_query(callback_query_id=call.id)
        send_current_movie(call=call)

    elif command == 'prev':
        users[chat_id]['current_discover_id'] -= 1
        # bot.answer_callback_query(callback_query_id=call.id)
        send_current_movie(call=call)


# ----- Вспомогательные функции -----

def send_help(chat_id):
    bot.send_message(chat_id=chat_id,
                     text=f'''1️⃣Чтобы бот начал работать, нажмите кнопку: <b>start</b>.
2️⃣Выберите, что вы хотите посмотреть и в зависимости от выбора нажмите кнопку: <b>фильм</b>, <b>мультфильм</b> или <b>сериал</b>.
3️⃣После того, как вы выбрали, что вы хотите посмотреть, вам будут предложены ещё две кнопки: <b>жанр</b> и <b>люди</b> (при нажатии на кнопку <b>жанр</b> - вы сможете выбрать жанр, а при нажатии кнопки <b>люди</b> - вы сможете выбрать актёра или режиссёра). Нажмите на любую из них и напишите любимый <b>жанр</b> или имя и фамилию <b>актёра</b> или <b>режиссёра</b>.Также, вы можете выбрать сразу пару критериев. Например, сначала выбрать <b>жанр</b>, а потом <b>актёра</b>,  и тогда при выборе фильма или сериала бот учтёт и то и то. Затем, бот предложит несколько <b>фильмов</b>, <b>мультфильмов</b> или <b>сериалов</b>, с выбранными вами критериями, выберите один из них, запаситесь вкусняшками и наслаждайтесь просмотром!\U0001F497
4️⃣Если вы хотите посмотреть просто какой-то популярный фильм, нажмите кнопку: <b>топ фильмов</b>.''',
                     parse_mode='HTML')


def send_first_movie(call):
    """Отправка первого сообщения с результатом поиска фильмов"""
    chat_id = call.message.chat.id
    users[chat_id]['current_discover_id'] = 0
    movie = users[chat_id]['discover'][0]
    message = call.message
    markup = InlineKeyboardMarkup()

    details_button = InlineKeyboardButton("Подробнее", callback_data=f'details_from_discover {movie.id}')
    if users[chat_id]['discover']['total_results'] > 1:
        markup.add(next_button)
    markup.add(details_button)
    if movie.poster_path is not None and movie.poster_path != '':
        movie_poster_url = str(tmdb.poster_w500_url + movie.poster_path)
    else:
        movie_poster_url = tmdb.poster_na_url
    bot.send_photo(chat_id=message.chat.id,
                   photo=movie_poster_url,
                   caption=views.cards.movie_short(
                       title=movie.title,
                       release_date=movie.release_date[:4],
                       vote_average=movie.vote_average),
                   parse_mode='HTML',
                   reply_markup=markup
                   )


def send_current_movie(call):
    """Редактирование сообщения для показа другого фильма из поиска"""
    chat_id = call.message.chat.id
    movie = users[chat_id]['discover'][users[chat_id]['current_discover_id']]
    message = call.message
    buttons = {'prev': {'callback_data': 'prev'},
               'next': {'callback_data': 'next'}}
    markup = quick_markup(buttons)

    details_button = InlineKeyboardButton("Подробнее", callback_data=f'details_from_discover {movie.id}')
    markup.add(details_button)
    media = InputMediaPhoto(tmdb.poster_w500_url + movie.poster_path,
                            caption=views.cards.movie_short(
                                title=movie.title,
                                release_date=movie.release_date[:4],
                                vote_average=movie.vote_average),
                            parse_mode='HTML')
    bot.edit_message_media(chat_id=message.chat.id,
                           message_id=message.id,
                           media=media,
                           reply_markup=markup
                           )
