import telebot
import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import tmdb
import views.cards

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

with open('secrets/telegram.key') as file:
    API_TOKEN = file.readline()
bot = telebot.TeleBot(API_TOKEN)


def run():
    bot.infinity_polling()


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, f"""\
Hi {message.from_user.first_name}, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


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


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)
