from time import sleep
from telepot import Bot
from threading import Thread
from pony.orm import db_session
from modules.database import User, Clip

with open('token.txt', 'r') as f:
    token = f.readline().strip()
    bot = Bot(token)


@db_session
def reply(msg):
    chatId = msg['from']['id']
    name = msg['from']['first_name']
    bot.sendMessage(chatId, "Hey, {}!\nI'm being developed, please wait...\n\nZzz... 😴".format(name))


def incoming_message(msg):
    Thread(target=reply, args=[msg]).start()

bot.message_loop({'chat': incoming_message})
while True:
    sleep(60)
