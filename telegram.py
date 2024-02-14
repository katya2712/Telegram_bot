import telebot
import logging

import tmdb

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
    for p in popular:
        bot.send_message(chat_id=message.chat.id,
                         text=f'''({p.title} ({p.release_date[:4]})
{p.overview}
Рейтинг: {round(p.vote_average * 10)}%''')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)
