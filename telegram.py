import telebot
import logging

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
        bot.send_photo(chat_id=message.chat.id,
                       photo=poster_w500_url+p.poster_path,
                       caption=views.cards.short(
                           title=p.title,
                           overview=p.overview,
                           release_date=p.release_date[:4],
                           vote_average=p.vote_average),
                       parse_mode='HTML'
                       )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)
