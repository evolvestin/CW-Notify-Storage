import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telebot
from telebot import types
import urllib3
import re
import requests
import time
from time import sleep
import datetime
from datetime import datetime
import _thread
import random

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds1 = ServiceAccountCredentials.from_json_keyfile_name('bigdata1.json', scope)
creds2 = ServiceAccountCredentials.from_json_keyfile_name('bigdata2.json', scope)
#creds3 = ServiceAccountCredentials.from_json_keyfile_name('worker5-storage.json', scope)
client1 = gspread.authorize(creds1)
client2 = gspread.authorize(creds2)
#client3 = gspread.authorize(creds3)
data1 = client1.open('storage-generator').worksheet('old2')
data2 = client2.open('eustgen').worksheet('old2')

bot = telebot.TeleBot('468445195:AAHKJxXQRxg5kJau_KT4smoCvJfnqcgOS4c')
idMe = 396978030
old2_ru = int(data1.cell(1, 1).value)
old2_eu = int(data2.cell(1, 1).value)
firstopen = 1
form_ru = 'Лот #(\d+) : (.*)\n' \
       'Продавец: (.*)\n' \
       'Текущая цена: (\d+) 👝\n' \
       'Покупатель: (.+)\n' \
       'Срок: (\d\d) (.*) (.*) (\d\d):(\d\d)\n' \
       'Статус: (#active|Finished|Cancelled|Failed)'
form_eu = 'Lot #(\d+) : (.*)\n' \
       'Seller: (.*)\n' \
       'Current price: (\d+) pouch\(es\)\n' \
       'Buyer: (.+)\n' \
       'End At: (\d\d) (.*) (.*) (\d\d):(\d\d)\n' \
       'Status: (#active|Finished|Cancelled|Failed)'
# ====================================================================================
bot.send_message(idMe, '👀')


def oldest_ru():
    while True:
        try:
            sleep(3)
            global data1
            global old2_ru
            goo = []
            text = requests.get('https://t.me/chatwars3/' + str(old2_ru))
            search = re.search(form_ru, str(text.text))
            if search:
                if str(search.group(11)) != '#active':
                    print('работаю https://t.me/chatwars3/' + str(old2_ru))
                    name = str(search.group(2))
                    ench = re.search('(⚡)\+(\d+) ', name)
                    enchanted = 'no'
                    if ench:
                        name = re.sub('⚡\+\d+ ', '', name)
                        enchanted = ench.group(2)
                    seller = search.group(3).split(' ')
                    castle_nick = seller[0] + '/' + seller[1]
                    status = search.group(11)
                    if status == 'Failed':
                        status = 'Cancelled'
                    goo.append(str(old2_ru) + '/' + str(search.group(1)) + '/' + enchanted + '/' + name + '/' + castle_nick
                               + '/' + search.group(4) + '/' + search.group(5) + '/' + search.group(6)
                               + '/' + search.group(7) + '/' + search.group(8) + '/' + search.group(9)
                               + '/' + search.group(10) + '/' + status)
                    old2_ru = old2_ru + 1
                    try:
                        data1.update_cell(1, 1, old2_ru)
                        data1.insert_row(goo, 2)
                    except:
                        creds1 = ServiceAccountCredentials.from_json_keyfile_name('bigdata1.json', scope)
                        client1 = gspread.authorize(creds1)
                        data1 = client1.open('storage-generator').worksheet('old2')
                        data1.update_cell(1, 1, old2_ru)
                        data1.insert_row(goo, 2)
                else:
                    print('https://t.me/chatwars3/' + str(old2_ru) + ' Активен, ничего не делаю')

        except Exception as e:
            bot.send_message(idMe, 'вылет oldest_ru')
            sleep(0.9)


def oldest_eu():
    while True:
        try:
            global firstopen
            if firstopen != 1:
                sleep(3)
            else:
                sleep(5)
                firstopen = 0
            global data1
            global old2_eu
            goo = []
            text = requests.get('https://t.me/ChatWarsAuction/' + str(old2_eu))
            search = re.search(form_eu, str(text.text))
            if search:
                if str(search.group(11)) != '#active':
                    print('работаю https://t.me/ChatWarsAuction/' + str(old2_eu))
                    name = str(search.group(2))
                    ench = re.search('(⚡)\+(\d+) ', name)
                    enchanted = 'no'
                    if ench:
                        name = re.sub('⚡\+\d+ ', '', name)
                        enchanted = ench.group(2)
                    seller = search.group(3).split(' ')
                    castle_nick = seller[0] + '/' + seller[1]
                    status = search.group(11)
                    if status == 'Failed':
                        status = 'Cancelled'
                    goo.append(str(old2_eu) + '/' + str(search.group(1)) + '/' + enchanted + '/' + name + '/' + castle_nick
                               + '/' + search.group(4) + '/' + search.group(5) + '/' + search.group(6)
                               + '/' + search.group(7) + '/' + search.group(8) + '/' + search.group(9)
                               + '/' + search.group(10) + '/' + status)
                    old2_eu = old2_eu + 1
                    try:
                        data2.update_cell(1, 1, old2_eu)
                        data2.insert_row(goo, 2)
                    except:
                        creds2 = ServiceAccountCredentials.from_json_keyfile_name('bigdata2.json', scope)
                        client2 = gspread.authorize(creds2)
                        data2 = client2.open('eustgen').worksheet('old2')
                        data2.update_cell(1, 1, old2_eu)
                        data2.insert_row(goo, 2)
                else:
                    print('https://t.me/ChatWarsAuction/' + str(old2_eu) + ' Активен, ничего не делаю')

        except Exception as e:
            bot.send_message(idMe, 'вылет oldest_eu')
            sleep(0.9)


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    if message.chat.id != idMe:
        bot.send_message(idMe, 'К тебе этот бот не имеет отношения, уйди пожалуйста')
    else:
        bot.send_message(idMe, 'Я работаю')


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    _thread.start_new_thread(oldest_ru, ())
    _thread.start_new_thread(oldest_eu, ())
    telepol()
