# -*- coding: utf-8 -*-
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
import dim

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
client1 = gspread.authorize(creds1)
data1 = client1.open(dim.file).worksheet('old')

bot = telebot.TeleBot(dim.token)
idMe = 396978030
ignore = str(data1.cell(1, 1).value)
old = int(data1.cell(2, 1).value)
ignore = ignore.split('/')
# ====================================================================================
bot.send_message(idMe, '🧐')


def my_time(search):
    day31 = 31 * 24 * 60 * 60
    day30 = 30 * 24 * 60 * 60
    day28 = 28 * 24 * 60 * 60
    stamp = int(datetime.now().timestamp())
    sec = ((stamp + (2 * 60 * 60) - 1530309600) * 3)
    if str(search.group(8)) == 'Wīndume':
        month = '10'
    elif str(search.group(8)) == 'Herbist':
        month = '11'
    elif str(search.group(8)) == 'Hailag':
        month = '12'
    elif str(search.group(8)) == 'Wintar':
        month = '01'
    elif str(search.group(8)) == 'Hornung':
        month = '02'
    elif str(search.group(8)) == 'Lenzin':
        month = '03'
    elif str(search.group(8)) == 'Ōstar':
        month = '04'
    elif str(search.group(8)) == 'Winni':
        month = '05'
    elif str(search.group(8)) == 'Brāh':
        month = '06'
    elif str(search.group(8)) == 'Hewi':
        month = '07'
    elif str(search.group(8)) == 'Aran':
        month = '08'
    elif str(search.group(8)) == 'Witu':
        month = '09'
    else:
        month = 'none'

    if month != 'none':
        day28 = 28 * 24 * 60 * 60
        seconds = 0 - (24 * 60 * 60)
        if int(search.group(9)) == 4:
            day28 = day28 + 24 * 60 * 60
        elif int(search.group(9)) > 4:
            seconds = seconds + 24 * 60 * 60
        seconds = seconds + day30 + day31 + 31536000 * (int(search.group(9)) - 1)  # Wīndume
        if int(month) == 1:
            seconds = seconds
        elif int(month) == 2:
            seconds = seconds + day31
        elif int(month) == 3:
            seconds = seconds + day31 + day28
        elif int(month) == 4:
            seconds = seconds + day31 + day28 + day31
        elif int(month) == 5:
            seconds = seconds + day31 + day28 + day31 + day30
        elif int(month) == 6:
            seconds = seconds + day31 + day28 + day31 + day30 + day31
        elif int(month) == 7:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30
        elif int(month) == 8:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31
        elif int(month) == 9:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31
        elif int(month) == 10:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30
        elif int(month) == 11:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31
            if int(search.group(9)) == 0:
                seconds = 0 - (24 * 60 * 60)
        elif int(month) == 12:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31 + day30
            if int(search.group(9)) == 0:
                seconds = day30 - (24 * 60 * 60)

        seconds = seconds + int(search.group(7)) * 24 * 60 * 60  # days
        seconds = seconds + int(search.group(10)) * 60 * 60  # hours
        seconds = seconds + int(search.group(11)) * 60  # minutes
        stack = int(stamp + (seconds - sec) / 3)
        return stack


def former(text):
    search = re.search(dim.form, str(text.text))
    goo = []
    if search:
        stamp = my_time(search)
        stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60
        if str(search.group(12)) != '#active' or (str(search.group(12)) == '#active' and stamp <= stamp_now):
            name = str(search.group(2))
            ench = re.search('(⚡)\+(\d+) ', name)
            enchanted = 'none'
            quality = 'none'
            if ench:
                name = re.sub('⚡\+\d+ ', '', name)
                enchanted = ench.group(2)
            if search.group(3):
                quality = search.group(3)
            seller = search.group(4).split(' ')
            castle_nick = seller[0] + '/' + seller[1]
            status = search.group(12)
            if status == 'Failed':
                status = 'Cancelled'
            elif status == '#active':
                status = 'Finished'
            goo.append(str(old) + '/' + str(search.group(1)) + '/' + enchanted + '/' + name + '/' + quality
                       + '/' + castle_nick + '/' + search.group(5) + '/' + search.group(6) + '/' + search.group(7)
                       + '/' + search.group(8) + '/' + search.group(9) + '/' + search.group(10)
                       + '/' + search.group(11) + '/' + status)
        else:
            goo.append('active')
    else:
        goo.append('false')
    return goo


def oldest():
    while True:
        try:
            sleep(3)
            global data1
            global old
            text = requests.get(dim.adress + str(old))
            print('работаю ' + dim.adress + str(old))
            if str(old) not in ignore:
                goo = former(text)
                if goo[0] == 'active':
                    print(dim.adress + str(old) + ' Активен, ничего не делаю')
                elif goo[0] == 'false':
                    print(dim.adress + str(old) + ' Форму не нашло')
                else:
                    old = old + 1
                    try:
                        data1.insert_row(goo, 3)
                        data1.update_cell(2, 1, old)
                    except:
                        creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
                        client1 = gspread.authorize(creds1)
                        data1 = client1.open(dim.file).worksheet('old')
                        data1.insert_row(goo, 3)
                        data1.update_cell(2, 1, old)
            else:
                print(dim.adress + str(old) + ' В черном списке, пропускаю')
                old = old + 1

        except Exception as e:
            bot.send_message(idMe, 'вылет oldest\n' + str(e))
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
    _thread.start_new_thread(oldest, ())
    telepol()
