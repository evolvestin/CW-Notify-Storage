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
import copy
from SQL import SQLighter
import dim

stamp1 = int(datetime.now().timestamp())
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
client1 = gspread.authorize(creds1)
data1 = client1.open(dim.file).worksheet('old')

bot = telebot.TeleBot(dim.token)
idMe = 396978030
ignore = str(data1.cell(1, 1).value)
old = str(data1.cell(2, 1).value)
old = old.split('/')
cock = int(old[1])
old = int(old[0])
check = 32
ignore = ignore.split('/')

# ====================================================================================


def timer(array):
    array[2] = array[2][3:]
    day31 = 31 * 24 * 60 * 60
    day30 = 30 * 24 * 60 * 60
    day28 = 28 * 24 * 60 * 60
    stamp = int(datetime.now().timestamp())
    sec = ((stamp + (2 * 60 * 60) - 1530309600) * 3)
    if str(array[1]) == 'Wīndume':
        month = '10'
    elif str(array[1]) == 'Herbist':
        month = '11'
    elif str(array[1]) == 'Hailag':
        month = '12'
    elif str(array[1]) == 'Wintar':
        month = '01'
    elif str(array[1]) == 'Hornung':
        month = '02'
    elif str(array[1]) == 'Lenzin':
        month = '03'
    elif str(array[1]) == 'Ōstar':
        month = '04'
    elif str(array[1]) == 'Winni':
        month = '05'
    elif str(array[1]) == 'Brāh':
        month = '06'
    elif str(array[1]) == 'Hewi':
        month = '07'
    elif str(array[1]) == 'Aran':
        month = '08'
    elif str(array[1]) == 'Witu':
        month = '09'
    else:
        month = 'none'

    if month != 'none':
        day28 = 28 * 24 * 60 * 60
        seconds = 0 - (24 * 60 * 60)
        if int(array[2]) == 4:
            day28 = day28 + 24 * 60 * 60
        elif int(array[2]) > 4:
            seconds = seconds + 24 * 60 * 60
        seconds = seconds + day30 + day31 + 31536000 * (int(array[2]) - 1)  # Wīndume
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
            if int(array[2]) == 0:
                seconds = 0 - (24 * 60 * 60)
        elif int(month) == 12:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31 + day30
            if int(array[2]) == 0:
                seconds = day30 - (24 * 60 * 60)

        seconds = seconds + int(array[0]) * 24 * 60 * 60  # days
        seconds = seconds + int(array[3]) * 60 * 60  # hours
        seconds = seconds + int(array[4]) * 60  # minutes
        stack = int(stamp + (seconds - sec) / 3)
        return stack


def log(stamp):
    if stamp == 0:
        stamp = int(datetime.now().timestamp())
    day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
    month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
    year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
    hours = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%H')
    minutes = datetime.utcfromtimestamp(int(stamp)).strftime('%M')
    seconds = datetime.utcfromtimestamp(int(stamp)).strftime('%S')
    message = str(day) + '.' + str(month) + '.' + str(year) + ' ' + str(hours) + ':' \
        + str(minutes) + ':' + str(seconds)
    return message


# ====================================================================================
bot.send_message(idMe, '🧐\n<code>' + log(stamp1) + '  -  ' + log(0) + '</code>', parse_mode='HTML')


def former(text, id, type):
    search = re.search(dim.form, str(text.text))
    goo = []
    if search:
        array = [search.group(7), search.group(8), search.group(9), search.group(10), search.group(11)]
        stamp = timer(array)
        stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60
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
        if len(seller) == 2:
            castle_nick = seller[0] + '/' + seller[1]
        else:
            nick = ''
            for j in seller:
                if seller.index(j) != 0:
                    nick += j + ' '
            nick = nick.rstrip()
            castle_nick = seller[0] + '/' + nick
        status = search.group(12)
        if status == 'Failed':
            status = 'Cancelled'
        text = str(id) + '/' + str(search.group(1)) + '/' + enchanted + '/' + name + '/' + quality \
            + '/' + castle_nick + '/' + search.group(5) + '/' + search.group(6) + '/' + search.group(7) \
            + '/' + search.group(8) + '/' + search.group(9) + '/' + search.group(10) + '/' + search.group(11) + '/'
        if type == 'old':
            if str(search.group(12)) != '#active' or (str(search.group(12)) == '#active' and stamp <= stamp_now):
                if status == '#active':
                    status = 'Finished'
                goo.append(text + status)
            else:
                goo.append('active')
        else:
            if str(search.group(12)) == '#active' and stamp >= stamp_now:
                goo.append(text + status)
            else:
                if status == '#active':
                    status = 'Finished'
                goo.append(text + status)
    else:
        goo.append('false')
    return goo


def former_old(text, id, type):
    search = re.search(dim.form, str(text.text))
    goo = []
    if search:
        array = [search.group(7), search.group(8), search.group(9), search.group(10), search.group(11)]
        stamp = timer(array)
        stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60
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
        text = str(id) + '/' + str(search.group(1)) + '/' + enchanted + '/' + name + '/' + quality \
            + '/' + castle_nick + '/' + search.group(5) + '/' + search.group(6) + '/' + search.group(7) \
            + '/' + search.group(8) + '/' + search.group(9) + '/' + search.group(10) + '/' + search.group(11) + '/'
        if type == 'old':
            if str(search.group(12)) != '#active' or (str(search.group(12)) == '#active' and stamp <= stamp_now):
                if status == '#active':
                    status = 'Finished'
                goo.append(text + status)
            else:
                goo.append('active')
        else:
            if str(search.group(12)) == '#active' and stamp >= stamp_now:
                goo.append(text + status)
            else:
                if status == '#active':
                    status = 'Finished'
                goo.append(text + status)
    else:
        goo.append('false')
    return goo


def checker():
    while True:
        try:
            global data1
            global old
            global cock
            print(log(0))
            creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
            client1 = gspread.authorize(creds1)
            data1 = client1.open(dim.file).worksheet('old')
            col = 1000
            cell_list = data1.range('A' + str(cock) + ':A' + str(cock + col))
            cock += col
            i = 1
            while (i % (col + 1)) != 0 and old >= 32:
                sleep(0.05)
                text = requests.get(dim.adress + str(old))
                print('работаю ' + dim.adress + str(old))
                if str(old) not in ignore:
                    goo = former(text, old, 'old')
                    if goo[0] == 'active':
                        print(dim.adress + str(old) + ' Активен, ничего не делаю')
                    elif goo[0] == 'false':
                        print(dim.adress + str(old) + ' Форму не нашло')
                    else:
                        cell_list[i - 1].value = goo[0]
                        old -= 1
                        i += 1
                else:
                    print(dim.adress + str(old) + ' В черном списке, пропускаю')
                    old -= 1
            if i > 1:
                string = str(old) + '/' + str(cock)
                try:
                    data1.update_cells(cell_list)
                    data1.update_cell(2, 1, string)
                except:
                    creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
                    client1 = gspread.authorize(creds1)
                    data1 = client1.open(dim.file).worksheet('old')
                    data1.update_cells(cell_list)
                    data1.update_cell(2, 1, string)
        except Exception as e:
            bot.send_message(idMe, 'вылет checker\n' + str(e))
            sleep(0.9)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    #_thread.start_new_thread(double_checker, ())
    _thread.start_new_thread(checker, ())
    telepol()
