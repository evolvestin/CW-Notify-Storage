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
old = int(data1.cell(2, 1).value)
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


db = SQLighter('old.db')
google = data1.col_values(1)
google.pop(0)
google.pop(0)
start_string = 'INSERT INTO old (auid, lotid, enchanted, name, quality, castle, seller, cost, buyer, stamp, status) ' \
    'VALUES '
string = ''
point = 0
for i in google:
    row = i.split('/')
    if len(row) > 1:
        timer_array = [row[9], row[10], row[11], row[12], row[13]]
        stamp = timer(timer_array)
        string += "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}'), ".format(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], stamp, row[14])
        point += 1
        if point == 1000:
            string = string.rstrip()
            string = string[:-1]
            string += ';'
            db.create_lots(start_string + string)
            string = ''
            point = 0
    else:
        print(google.index(i))
        continue
if string != '':
    string = string.rstrip()
    string = string[:-1]
    string += ';'
    db.create_lots(start_string + string)
    string = ''


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


def former(text):
    search = re.search(dim.form, str(text.text))
    goo = []
    if search:
        array = [search.group(7), search.group(8), search.group(9), search.group(10), search.group(11)]
        stamp = timer(array)
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
            db = SQLighter('old.db')
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
                    row = goo[0].split('/')
                    stamp = timer([row[9], row[10], row[11], row[12], row[13]])
                    db.create_lot(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], stamp, row[14])
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


def messages():
    while True:
        try:
            global i
            db = SQLighter('old.db')
            creds2 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_storage, scope)
            client2 = gspread.authorize(creds2)
            data2 = client2.open('Active-Info').worksheet('const')
            const = data2.col_values(2)
            data2 = client2.open(dim.file).worksheet('storage')
            print('начался')
            i = 0
            while i < len(const):
                text = ''
                time_30 = int(datetime.now().timestamp()) - (7*24*60*60)
                newcol = []
                newcol_30 = []
                unsold = []
                f_average = 0
                average_30 = 0
                f_un_average = 0
                un_average_30 = 0
                f_min = 1000
                f_max = 0
                min_30 = 1000
                max_30 = 0
                col = db.get_lots(const[i])
                if str(col) != 'False':
                    for z in col:
                        cost = z[7]
                        buyer = z[8]
                        stamp = z[9]
                        status = z[10]
                        if status != 'Cancelled':
                            if buyer != 'None':
                                if stamp >= time_30:
                                    newcol_30.append(cost)
                                    average_30 += cost
                                    if min_30 > cost:
                                        min_30 = cost
                                    if max_30 < cost:
                                        max_30 = cost
                                newcol.append(cost)
                                f_average += cost
                                if f_min > cost:
                                    f_min = cost
                                if f_max < cost:
                                    f_max = cost
                            else:
                                if stamp >= time_30:
                                    un_average_30 += 1
                                unsold.append(cost)
                                f_un_average += 1

                    if len(newcol) > 0:
                        last = newcol[len(newcol) - 1]
                        lastsold = '\nПоследний проданный: ' + str(last)
                        print('i = ' + str(i) + ' last = ' + str(last))
                    else:
                        lastsold = ''

                    newcol.sort()
                    newcol_30.sort()

                    if len(newcol) % 2 == 0 and len(newcol) != 0:
                        lot1 = int(newcol[len(newcol) // 2])
                        lot2 = int(newcol[len(newcol) // 2 - 1])
                        median = round((lot1 + lot2) / 2, 2)
                    elif len(newcol) == 0:
                        median = 0
                    else:
                        median = int(newcol[len(newcol) // 2])

                    if len(newcol_30) % 2 == 0 and len(newcol_30) != 0:
                        lot1_30 = int(newcol_30[len(newcol_30) // 2])
                        lot2_30 = int(newcol_30[len(newcol_30) // 2 - 1])
                        median_30 = round((lot1_30 + lot2_30) / 2, 2)
                    elif len(newcol_30) == 0:
                        median_30 = 0
                    else:
                        median_30 = int(newcol_30[len(newcol_30) // 2])

                    if len(newcol) > 0:
                        f_average = round(f_average / len(newcol), 2)
                    else:
                        f_average = 0
                    if len(newcol_30) > 0:
                        average_30 = round(average_30 / len(newcol_30), 2)
                    else:
                        average_30 = 0

                else:
                    median = 0
                    median_30 = 0
                    lastsold = ''

                if f_min == 1000:
                    f_min = 0
                if min_30 == 1000:
                    min_30 = 0

                text = text + '\n\n<b>Продано раз: </b>' + str(len(newcol)) + '\n\n' \
                    '<b>За всё время:</b>\n' \
                    'Медианная цена: ' + str(median) + '\n' \
                    'Средняя цена: ' + str(f_average) + '\n' \
                    'Мин/Макс: ' + str(f_min) + '/' + str(f_max) + '\n' \
                    'Не продано: ' + str(f_un_average) + '/' + str(len(newcol) + f_un_average) + '\n\n' + \
                    '<b>За последние 7 дней:</b>\n' + \
                    'Медианная цена: ' + str(median_30) + '\n' \
                    'Средняя цена: ' + str(average_30) + '\n' \
                    'Мин/Макс: ' + str(min_30) + '/' + str(max_30) + '\n' \
                    'Не продано: ' + str(un_average_30) + '/' + str(len(newcol_30) + un_average_30) + \
                    str(lastsold) + '\n\n'

                try:
                    data2.update_cell(1, i + 1, const[i])
                    data2.update_cell(2, i + 1, text)
                except:
                    creds2 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_storage, scope)
                    client2 = gspread.authorize(creds2)
                    data2 = client2.open(dim.file).worksheet('storage')
                    data2.update_cell(1, i + 1, const[i])
                    data2.update_cell(2, i + 1, text)
                sleep(2)
                i = i + 1

            sleep(60)
            print('заснул')
        except Exception as e:
            print('i = ' + str(i))
            print('вылетел')
            sleep(1)


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
    _thread.start_new_thread(messages, ())
    telepol()
