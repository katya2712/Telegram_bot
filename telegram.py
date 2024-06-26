import os

import telebot
import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    InputMediaPhoto
from telebot.util import quick_markup

import chat
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
#   'popular': [],
# 	'genre_id': '',
# 	'current_discover_id': 0
#   'current_popular_id': 0
#   'messages': []
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
    # создаем словарь для каждого пользователя
    clear_user_state(chat_id, clear_messages=True)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton('\U0001F3A5Фильм')
    item2 = KeyboardButton('\U0001F36DМультфильм')
    item3 = KeyboardButton('\U0001F51DТоп фильмов')
    item5 = KeyboardButton('\U0001F198Помощь')
    markup.add(item1, item2, item3, item5)
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
def send_popular(message):
    """Список популярных фильмов на сегодня"""
    chat_id = message.chat.id
    # создаем словарь для каждого пользователя
    clear_user_state(chat_id)

    users[chat_id]['popular'] = tmdb.popular()
    send_first_popular(message=message)


# Поиск фильмов по названию
@bot.message_handler(commands=['кино', 'movie'])
def search_movie(message):
    print(message)
    args = ' '.join(message.text.split()[1:])
    movies = tmdb.movie_search(args)
    if movies.total_results > 0:
        for movie in movies:
            print(movie)
            movie_poster_url = get_movie_poster_url(movie)
            bot.send_photo(chat_id=message.chat.id,
                           photo=movie_poster_url,
                           caption=views.cards.movie_short(
                               title=movie.title,
                               release_date=movie.release_date[:4],
                               vote_average=movie.vote_average),
                           parse_mode='HTML'
                           # reply_markup=markup
                           )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=f'По запросу "{message.text}" ничего не найдено.')


# Поиск фильмов
@bot.message_handler(func=lambda message: message.text == '\U0001F3A5Фильм')
def send_genres_handler(message):
    """Отправляет пользователю список доступных жанров фильмов"""
    chat_id = message.chat.id
    # создаем словарь для каждого пользователя
    clear_user_state(chat_id)

    buttons = {}
    for genre in tmdb.genres:
        buttons[genre.name] = {'callback_data': f'genre_id {genre.id} {genre.name}'}
    markup = quick_markup(buttons, row_width=3)
    bot.send_message(chat_id=chat_id,
                     text='<b>Выберите жанр:</b>',
                     parse_mode='HTML',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '\U0001F36DМультфильм')
def send_mult_handler(message):
    chat_id = message.chat.id
    # создаем словарь для каждого пользователя
    clear_user_state(chat_id)
    users[chat_id]['genre_id'] = tmdb.mult_id
    bot.send_message(chat_id=chat_id,
                     text=f'Ищем мультфильмы.\nНапишите имя актёра озвучивания или режиссёра.')


# Список популярных фильмов
@bot.message_handler(func=lambda message: message.text == '\U0001F51DТоп фильмов')
def send_popular_handler(message):
    send_popular(message)


@bot.message_handler(func=lambda message: message.chat.id in users and users[message.chat.id]['genre_id'] != '')
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
            films = ', '.join([film.title for film in person.known_for if hasattr(film, 'title')])
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


# Общение с groqAI
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.chat.id
    if chat_id not in users or 'messages' not in users[chat_id]:
        clear_user_state(chat_id, clear_messages=True)
    users[chat_id]['messages'].append({"role": 'user', "content": message.text})
    context = chat.get_response(users[chat_id]['messages'])
    bot.send_message(chat_id=chat_id,
                     text=context[-1]['content'],
                     parse_mode='Markdown')
    users[chat_id]['messages'] = context


# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     text = f'Неизвестная команда "{message.text}"'
#     bot.reply_to(message=message, text=text)


# ----- Обработчики колбэков из кнопок -----

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

        buttons = {}
        # добавляем кнопку "предыдущий", если фильм не первый
        if users[chat_id]['current_discover_id'] > 0:
            buttons['prev'] = {'callback_data': 'prev'}
        # добавляем кнопку "следующий", если фильм не последний
        if users[chat_id]['current_discover_id'] < movie_count - 1:
            buttons['next'] = {'callback_data': 'next'}
        markup = quick_markup(buttons)

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

    if command == 'details_from_popular':
        movie = tmdb.movie_details(args)
        movie_count = len(users[chat_id]['popular'])
        genres = [genres['name'] for genres in movie.genres]

        buttons = {}
        # добавляем кнопку "предыдущий", если фильм не первый
        if users[chat_id]['current_popular_id'] > 0:
            buttons['prev'] = {'callback_data': 'prev'}
        # добавляем кнопку "следующий", если фильм не последний
        if users[chat_id]['current_popular_id'] < movie_count - 1:
            buttons['next'] = {'callback_data': 'next'}
        markup = quick_markup(buttons)

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
        genre_name = ' '.join(args[1:])
        bot.answer_callback_query(callback_query_id=call.id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'Выбран жанр {genre_name}.\nНапишите имя актёра или режиссёра')

    elif command == 'select_person':
        users[chat_id]['discover'] = tmdb.discover(genre_id=users[chat_id]['genre_id'],
                                                   people_id=args,
                                                   )
        bot.answer_callback_query(callback_query_id=call.id)
        if users[chat_id]['discover']['total_results'] > 0:
            send_first_movie(call=call)
        else:
            bot.send_message(chat_id=chat_id,
                             text='По вашему запросу ничего не найдено. Пожалуйста, повторите поиск.')

    elif command == 'next':
        # если не пуст список поиска
        if users[chat_id]['discover']:
            users[chat_id]['current_discover_id'] += 1
            send_current_movie(call=call)
        # если не пуст список популярных
        elif users[chat_id]['popular']:
            users[chat_id]['current_popular_id'] += 1
            send_current_popular(call=call)

    elif command == 'prev':
        # если не пуст список поиска
        if users[chat_id]['discover']:
            users[chat_id]['current_discover_id'] -= 1
            send_current_movie(call=call)
        elif users[chat_id]['popular']:
            users[chat_id]['current_popular_id'] -= 1
            send_current_popular(call=call)


# ----- Вспомогательные функции -----


def send_help(chat_id):
    bot.send_message(chat_id=chat_id,
                     text=f'''1️⃣Чтобы бот начал работать, нажмите кнопку: <b>start</b>.
2️⃣Выберите, что вы хотите посмотреть и в зависимости от выбора нажмите кнопку: <b>фильм</b> или <b>мультфильм</b>.
3️⃣Если вы выбрали смотреть <b>фильм</b>, бот предложит выбрать жанр (вам будет предложено множество кнопок с названиями жанров), нажмите на одну из них. Затем, вы должны написать имя и фамилию <b>актёра</b> или <b>режиссёра</b>. После этого бот предложит список фильмов с заданными критериями. Если вы выбрали смотреть <b>мультфильм</b>, то после нажатия на кнопку просто напишите имя и фамилию <b>актёра озвучивания</b> или <b>режиссёра</b>. После этого бот предложит список мультфильмов с заданными критериями.
4️⃣Если вы хотите посмотреть просто какой-то популярный фильм, нажмите кнопку: <b>топ фильмов</b> и тогда бот предложит вам список самых популярных фильмов на сегодняшний день.\U0001F497''',
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
    movie_poster_url = get_movie_poster_url(movie)
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
    movie_count = len(users[chat_id]['discover'])
    message = call.message

    buttons = {}
    # добавляем кнопку "предыдущий", если фильм не первый
    if users[chat_id]['current_discover_id'] > 0:
        buttons['prev'] = {'callback_data': 'prev'}
    # добавляем кнопку "следующий", если фильм не последний
    if users[chat_id]['current_discover_id'] < movie_count - 1:
        buttons['next'] = {'callback_data': 'next'}
    markup = quick_markup(buttons)

    details_button = InlineKeyboardButton("Подробнее", callback_data=f'details_from_discover {movie.id}')
    markup.add(details_button)

    movie_poster_url = get_movie_poster_url(movie)
    media = InputMediaPhoto(movie_poster_url,
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


def send_first_popular(message):
    """Отправка первого сообщения с результатом популярных фильмов"""
    chat_id = message.chat.id
    users[chat_id]['current_popular_id'] = 0
    movie = users[chat_id]['popular'][0]
    markup = InlineKeyboardMarkup()

    details_button = InlineKeyboardButton("Подробнее", callback_data=f'details_from_popular {movie.id}')
    markup.add(next_button)
    markup.add(details_button)
    movie_poster_url = get_movie_poster_url(movie)
    bot.send_photo(chat_id=message.chat.id,
                   photo=movie_poster_url,
                   caption=views.cards.movie_short(
                       title=movie.title,
                       release_date=movie.release_date[:4],
                       vote_average=movie.vote_average),
                   parse_mode='HTML',
                   reply_markup=markup
                   )


def send_current_popular(call):
    """Редактирование сообщения для показа другого фильма из списка популярных"""
    chat_id = call.message.chat.id
    movie = users[chat_id]['popular'][users[chat_id]['current_popular_id']]
    movie_count = len(users[chat_id]['popular'])
    message = call.message

    buttons = {}
    # добавляем кнопку "предыдущий", если фильм не первый
    if users[chat_id]['current_popular_id'] > 0:
        buttons['prev'] = {'callback_data': 'prev'}
    # добавляем кнопку "следующий", если фильм не последний
    if users[chat_id]['current_popular_id'] < movie_count - 1:
        buttons['next'] = {'callback_data': 'next'}
    markup = quick_markup(buttons)

    details_button = InlineKeyboardButton("Подробнее", callback_data=f'details_from_popular {movie.id}')
    markup.add(details_button)

    movie_poster_url = get_movie_poster_url(movie)
    media = InputMediaPhoto(movie_poster_url,
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


def get_movie_poster_url(movie):
    print(movie)
    if movie.poster_path is not None and movie.poster_path != '':
        return str(tmdb.poster_w500_url + movie.poster_path)
    else:
        return tmdb.poster_na_url


def clear_user_state(chat_id, clear_messages=False):
    users[chat_id] = {}
    users[chat_id]['discover'] = []
    users[chat_id]['popular'] = []
    users[chat_id]['genre_id'] = ''
    users[chat_id]['current_discover_id'] = 0
    users[chat_id]['current_popular_id'] = 0
    if clear_messages:
        users[chat_id]['messages'] = []
