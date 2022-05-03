import os
from threading import Thread
import requests

import telebot
from lxml import html
import schedule
from models import DigitakaUrls
from pony.orm import db_session, select

credentials = os.getenv('API_CREDENTIALS')
bot = telebot.TeleBot(credentials)


@bot.message_handler(content_types=['text'])
@db_session
def get_text_messages(message):
    DigitakaUrls(user_id=message.from_user.id, url=message.text)
    message_to_user = 'Сохранил ваш запрос. Как только товар будет доступен, я сообщу. Хорошего дня!'
    bot.send_message(message.from_user.id, message_to_user)


def check_url(url):
    tree = html.fromstring(requests.get(url).text)
    item_lxml = tree.xpath('//tr[th[text()="Buy"]]/td/text()')[0]
    if 'Sorry, No Stock' in item_lxml:
        return False
    return True


@db_session
def check():
    item_requests = select(item for item in DigitakaUrls)
    for item_request in item_requests:
        user = item_request.user_id
        item_url = item_request.url
        if check_url(item_url):
            good_message = f'Товар теперь доступен.\n{item_url}'
            bot.send_message(user, good_message)
            DigitakaUrls.select(lambda item: item.url == item_url).delete(bulk=True)


def schedule_checker():
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    schedule.every(60).seconds.do(check)
    Thread(target=schedule_checker).start()
    bot.polling(none_stop=True, interval=0)
