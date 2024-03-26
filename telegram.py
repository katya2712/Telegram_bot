import telebot
import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    InputMediaPhoto
from telebot.util import quick_markup

import tmdb
import utils
import variables
import views.cards

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

search_type = 'movie'
discover = []
prev_button = InlineKeyboardButton("prev", callback_data=f'prev')
next_button = InlineKeyboardButton("next", callback_data=f'next')


def send_help(chat_id):
    bot.send_message(chat_id=chat_id,
                     text=f'''1️⃣Чтобы бот начал работать, нажмите кнопку: <b>start</b>.
2️⃣Выберите, что вы хотите посмотреть и в зависмости от выбора нажмите кнопку: <b>фильм</b>, <b>мультфильм</b> или <b>сериал</b>.
3️⃣После того, как вы выбрали, что вы хотите посмотреть, вам будут предложены ещё две кнопки: <b>жанр</b> и <b>люди</b> (при нажатии на кнопку <b>жанр</b> - вы сможете выбрать жанр, а при нажатии кнопки <b>люди</b> - вы сможете выбрать актёра или режиссёра). Нажмите на любую из них и напишите любимый <b>жанр</b> или имя и фамилию <b>актёра</b> или <b>режиссёра</b>.Также, вы можете выбрать сразу пару критериев. Например, сначала выбрать <b>жанр</b>, а потом <b>актёра</b>,  и тогда при выборе фильма или сериала бот учтёт и то и то. Затем, бот предложит несколько <b>фильмов</b>, <b>мультфильмов</b> или <b>сериалов</b>, с выбранными вами критериями, выберите один из них, запаситесь вкусняшками и наслаждайтесь просмотром!\U0001F497
4️⃣Если вы хотите посмотреть просто какой-то популярный фильм, нажмите кнопку: <b>топ фильмов</b>.''',
                     parse_mode='HTML')


with open('secrets/telegram.key') as file:
    API_TOKEN = file.readline()
    bot = telebot.TeleBot(API_TOKEN)


def run():
    bot.infinity_polling()


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # item1 = KeyboardButton('/\U0001F198Помощь')
    # item2 = KeyboardButton('/\U0001F3A5Фильм')
    # item3 = KeyboardButton('/\U0001F3ADМультфильм')
    # item4 = KeyboardButton('/\U0001F3ACСериал')
    # item5 = KeyboardButton('/\U0001F51DТоп_фильмов')
    item1 = KeyboardButton('\U0001F3A5Фильм')
    item2 = KeyboardButton('\U0001F51DТоп фильмов')
    item5 = KeyboardButton('\U0001F198Помощь')
    markup.add(item1, item2, item5)
    bot.send_message(message.chat.id,
                     f'''Привет,{message.from_user.first_name}!\U0001F44B
Рады видеть тебя в нашем боте. Не будем долго болтать и приступим к выбору занятия на вечер!

Скорее выбирай,что ты хочешь посмотреть.\U0001F447\U0001F447\U0001F447''',
                     reply_markup=markup)


@bot.message_handler(commands=['help', '\U0001F198Помощь'])
def movie_selection(message):
    send_help(message.chat.id)
    bot.send_message(message.chat.id,
                     f'''1️⃣Чтобы бот начал работать, нажмите кнопку: <b>start</b>.
2️⃣Выберите, что вы хотите посмотреть и в зависмости от выбора нажмите кнопку: <b>фильм</b>, <b>мультфильм</b> или <b>сериал</b>.
3️⃣После того, как вы выбрали, что вы хотите посмотреть, вам будут предложены ещё три кнопки: <b>жанр</b>, <b>актёр</b> и <b>режиссёр</b>. Нажмите на любую из них и напишите любимый <b>жанр</b>, <b>актёра</b> или <b>режиссёра</b>.Также, вы можете выбрать сразу пару критериев. Например, сначала выбрать <b>жанр</b>, а потом <b>актёра</b>,  и тогда при выборе фильма или сериала бот учтёт и то и то. Затем, бот предложит несколько <b>фильмов</b>, <b>мультфильмов</b> или <b>сериалов</b>, с выбранными вами критериями, выберите один из них, запаситесь вкусняшками и наслаждайтесь просмотром!\U0001F497
4️⃣Если вы хотите посмотреть просто какой-то популярный фильм, нажмите кнопку: <b>топ фильмов</b>.''',
                     parse_mode='HTML')


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
                     f'''Выбирай\U0001F447\U0001F447\U0001F447:''',
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
                     f'''Выбирай\U0001F447\U0001F447\U0001F447:''',
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
                     f'''Выбирай\U0001F447\U0001F447\U0001F447:''',
                     reply_markup=markup)


@bot.message_handler(commands=['person', 'люди'])
def send_person(message):
    """Поиск людей"""
    arg = utils.remove_first_word(message.text)
    persons = tmdb.person_search(arg)
    if persons.total_results > 0:
        text = ''
        for person in persons:
            text += f'id: {person.id}, имя: {person.name}\n'
        bot.send_message(chat_id=message.chat.id,
                         text=text)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f'По запросу "{arg}" ничего не найдено, введите заново имя и фамилию актёра или режиссёра. ')


# Список популярных фильмов на сегодня
@bot.message_handler(commands=['popular'])
def send_popular(message):
    popular = tmdb.popular()
    # постер с шириной 500px

    for p in popular:
        markup = InlineKeyboardMarkup()
        details_button = InlineKeyboardButton("Подробнее", callback_data=f'details {p.id}')
        markup.add(details_button)
        bot.send_photo(chat_id=message.chat.id,
                       photo=tmdb.poster_w500_url + p.poster_path,
                       caption=views.cards.movie_short(
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
        buttons[genre.name] = {'callback_data': f'genre_id {genre.id} {genre.name}'}
    markup = quick_markup(buttons, row_width=3)
    bot.send_message(chat_id=message.chat.id,
                     text=f'<b>Выберите жанр:</b>',
                     parse_mode='HTML',
                     reply_markup=markup)


@bot.message_handler(commands=['discover'])
def send_discover_result(message):
    discover = tmdb.discover(12, 85)

    for d in discover:
        markup = InlineKeyboardMarkup()
        details_button = InlineKeyboardButton("Подробнее", callback_data=f'details {d.id}')
        markup.add(details_button)
        bot.send_photo(chat_id=message.chat.id,
                       photo=tmdb.poster_w500_url + d.poster_path,
                       caption=views.cards.movie_short(
                           title=d.title,
                           overview=d.overview,
                           release_date=d.release_date[:4],
                           vote_average=d.vote_average),
                       parse_mode='HTML',
                       reply_markup=markup
                       )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    global discover
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
        movie_count = len(discover)
        genres = [genres['name'] for genres in movie.genres]
        markup = InlineKeyboardMarkup()

        # добавляем кнопку "предыдущий", если фильм не первый
        if variables.current_discover_id > 0:
            markup.add(prev_button)

        # добавляем кнопку "следующий", если фильм не последний
        if variables.current_discover_id < movie_count - 1:
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
        variables.genre_id = args[0]
        genre_name = ' '.join(args[1:])
        bot.answer_callback_query(callback_query_id=call.id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'Выбран жанр {genre_name}\n.Напишите имя актёра или режисёра')
    elif command == 'select_person':
        discover = tmdb.discover(genre_id=variables.genre_id, people_id=args)
        # постер с шириной 500px
        send_first_movie(call=call)

        # for movie in discover:
        #     markup = InlineKeyboardMarkup()
        #     details_button = InlineKeyboardButton("Подробнее", callback_data=f'details {args}')
        #     markup.add(details_button)
        #     bot.send_photo(chat_id=call.message.chat.id,
        #                    photo=tmdb.poster_w500_url + movie.poster_path,
        #                    caption=views.cards.movie_short(
        #                        title=movie.title,
        #                        overview=movie.overview,
        #                        release_date=movie.release_date[:4],
        #                        vote_average=movie.vote_average),
        #                    parse_mode='HTML',
        #                    reply_markup=markup
        #                    )
    elif command == 'next':
        variables.current_discover_id += 1
        send_current_movie(call=call)
    elif command == 'prev':
        variables.current_discover_id -= 1
        send_current_movie(call=call)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text[0] == '@':
        # Удалить?
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
    elif message.text == '\U0001F198Помощь':
        # Вызов помощи из клавиатуры
        send_help(message.chat.id)
    elif message.text == '\U0001F3A5Фильм':
        send_genres(message)
    elif message.text == '\U0001F51DТоп фильмов':
        send_popular(message)
    elif variables.genre_id != '':
        # Если выбран жанр, любое текствое сообщение трактуем как поиск персоны (актера или режисёра)
        # Выполняется если не обнаружена другая команда
        persons = tmdb.person_search(message.text)
        if persons.total_results > 0:
            # text = ''
            for person in persons:
                details = tmdb.person_details(person.id)
                markup = InlineKeyboardMarkup()
                select_button = InlineKeyboardButton("Выбрать", callback_data=f'select_person {person.id}')
                markup.add(select_button)
                bot.send_message(chat_id=message.chat.id,
                                 text=views.cards.person_short(name=person.name,
                                                               biography=details.biography,
                                                               date_of_birth=details.birthday,
                                                               ),
                                 reply_markup=markup,
                                 parse_mode='HTML')
        # poster_w500_url = (tmdb.info().images['secure_base_url'] +
        #                    tmdb.info().images['poster_sizes'][-3])
        #
        # for p in popular:
        #     markup = InlineKeyboardMarkup()
        #     details_button = InlineKeyboardButton("Подробнее", callback_data=f'details {p.id}')
        #     markup.add(details_button)
        #     bot.send_photo(chat_id=message.chat.id,
        #                    photo=poster_w500_url + p.poster_path,
        #                    caption=views.cards.movie_short(
        #                        title=p.title,
        #                        overview=p.overview,
        #                        release_date=p.release_date[:4],
        #                        vote_average=p.vote_average),
        #                    parse_mode='HTML',
        #                    reply_markup=markup
        #                    )
        else:
            bot.send_message(chat_id=message.chat.id,
                             text=f'По запросу "{message.text}" ничего не найдено, введите заново имя и фамилию актёра или режиссёра.')

    else:
        # доделать обработчик неизвестных команд
        bot.reply_to(message, message.text)


def send_first_movie(call):
    variables.current_discover_id = 0
    movie = discover[0]
    message = call.message
    markup = InlineKeyboardMarkup()

    details_button = InlineKeyboardButton("Подробнее", callback_data=f'details_from_discover {movie.id}')
    markup.add(next_button, details_button)
    bot.send_photo(chat_id=message.chat.id,
                   photo=tmdb.poster_w500_url + movie.poster_path,
                   caption=views.cards.movie_short(
                       title=movie.title,
                       overview=movie.overview,
                       release_date=movie.release_date[:4],
                       vote_average=movie.vote_average),
                   parse_mode='HTML',
                   reply_markup=markup
                   )


def send_current_movie(call):
    movie_count = len(discover)
    movie = discover[variables.current_discover_id]
    message = call.message
    markup = InlineKeyboardMarkup()

    # добавляем кнопку "предыдущий", если фильм не первый
    if variables.current_discover_id > 0:
        markup.add(prev_button)

    # добавляем кнопку "следующий", если фильм не последний
    if variables.current_discover_id < movie_count - 1:
        markup.add(next_button)

    details_button = InlineKeyboardButton("Подробнее", callback_data=f'details_from_discover {movie.id}')
    markup.add(details_button)
    media = InputMediaPhoto(tmdb.poster_w500_url + movie.poster_path,
                            caption=views.cards.movie_short(
                                title=movie.title,
                                overview=movie.overview,
                                release_date=movie.release_date[:4],
                                vote_average=movie.vote_average),
                            parse_mode='HTML')
    bot.edit_message_media(chat_id=message.chat.id,
                           message_id=message.id,
                           media=media,
                           reply_markup=markup
                           )
