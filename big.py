# -*- coding: utf-8 -*-
import re
import dim
import sys
import time
import copy
import _thread
import telebot
import gspread
import requests
import datetime
import traceback
from time import sleep
from telebot import types
from SQL import SQLighter
from bs4 import BeautifulSoup
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials


stamp1 = int(datetime.now().timestamp())
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
client1 = gspread.authorize(creds1)
data1 = client1.open(dim.file).worksheet('old')

bot = telebot.TeleBot(dim.token)
idMe = 396978030
# ====================================================================================


def timer(search):
    s_day = int(search.group(1))
    s_month = str(search.group(2))
    s_year = int(search.group(3)) - 60
    s_hour = int(search.group(4))
    s_minute = int(search.group(5))
    stamp = int(datetime.now().timestamp())
    sec = ((stamp + (dim.server * 60 * 60) - 1530309600) * 3)
    if s_month == 'Wintar':
        month = 1
    elif s_month == 'Hornung':
        month = 2
    elif s_month == 'Lenzin':
        month = 3
    elif s_month == 'Ōstar':
        month = 4
    elif s_month == 'Winni':
        month = 5
    elif s_month == 'Brāh':
        month = 6
    elif s_month == 'Hewi':
        month = 7
    elif s_month == 'Aran':
        month = 8
    elif s_month == 'Witu':
        month = 9
    elif s_month == 'Wīndume':
        month = 10
    elif s_month == 'Herbist':
        month = 11
    elif s_month == 'Hailag':
        month = 12
    else:
        month = 0

    if month != 0:
        day31 = 31 * 24 * 60 * 60
        day30 = 30 * 24 * 60 * 60
        day28 = 28 * 24 * 60 * 60
        seconds = 0 - (24 * 60 * 60)
        if s_year == 4:
            day28 = day28 + 24 * 60 * 60
        elif s_year > 4:
            seconds = seconds + 24 * 60 * 60
        seconds = seconds + day30 + day31 + 31536000 * (s_year - 1)  # Wīndume
        if month == 1:
            seconds = seconds
        elif month == 2:
            seconds = seconds + day31
        elif month == 3:
            seconds = seconds + day31 + day28
        elif month == 4:
            seconds = seconds + day31 + day28 + day31
        elif month == 5:
            seconds = seconds + day31 + day28 + day31 + day30
        elif month == 6:
            seconds = seconds + day31 + day28 + day31 + day30 + day31
        elif month == 7:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30
        elif month == 8:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31
        elif month == 9:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31
        elif month == 10:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30
        elif month == 11:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31
            if s_year == 0:
                seconds = 0 - (24 * 60 * 60)
        elif month == 12:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31 + day30
            if s_year == 0:
                seconds = day30 - (24 * 60 * 60)

        seconds = seconds + s_day * 24 * 60 * 60
        seconds = seconds + s_hour * 60 * 60
        seconds = seconds + s_minute * 60
        stack = int(stamp + (seconds - sec) / 3)
        return stack


def form_mash(lot):
    lotid = 0
    stamp = 0
    name = 'none'
    cost = 'none'
    buyer = 'none'
    status = 'none'
    seller = 'none'
    quality = 'none'
    enchanted = 'none'
    condition = 'none'
    lot = re.sub('\'', '&#39;', lot)
    stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60
    splited = lot.split('/')
    for g in splited:
        title = re.search(dim.title, g)
        quali = re.search(dim.quali, g)
        condi = re.search(dim.condi, g)
        price = re.search(dim.price, g)
        sell = re.search(dim.seller, g)
        whobuy = re.search(dim.buys, g)
        ptime = re.search(dim.stamp, g)
        stat = re.search(dim.status, g)
        if title:
            lotid = title.group(1)
            name = re.sub(' \+\d+[⚔🛡💧]', '', title.group(2))
            ench = re.search('(⚡)\+(\d+) ', name)
            enchanted = 'none'
            if ench:
                name = re.sub('⚡\+\d+ ', '', name)
                enchanted = ench.group(2)
        if quali:
            quality = quali.group(1)
        if condi:
            condition = re.sub(' ⏰.*', '', condi.group(1))
        if sell:
            seller = sell.group(1)
        if price:
            cost = int(price.group(1))
        if whobuy:
            buyer = whobuy.group(1)
        if ptime:
            stamp = timer(ptime)
        if stat:
            status = stat.group(1)
            if status == 'Failed':
                status = 'Cancelled'
            if status == '#active':
                if stamp < stamp_now:
                    status = 'Finished'
    return [splited[0], lotid, enchanted, name, quality, condition, seller, cost, buyer, stamp, status]


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


start_string = 'INSERT INTO old (auid, lotid, enchanted, name, quality, ' \
               'condition, seller, cost, buyer, stamp, status) VALUES '
stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60
google = data1.col_values(1)
db = SQLighter('old.db')
ignore = str(google[0])
ignore = ignore.split('/')
old = int(google[1])
new = copy.copy(old)
check = copy.copy(old)
firstopen = 1
google.pop(0)
google.pop(0)
string = ''
point = 0
perk = 3
# ====================================================================================
start_message = bot.send_message(idMe, '<code>' + log(stamp1) + '\n' + log(0) + '</code>', parse_mode='HTML')


for i in google:
    perk += 1
    if len(i) > 0:
        row = form_mash(i)
        string += "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}'), "\
            .format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        point += 1
        if point == 1000:
            string = string.rstrip()
            string = string[:-1]
            string += ';'
            db.create_lots(start_string + string)
            string = ''
            point = 0
    else:
        bot.send_message(idMe, 'В базе ' + dim.file + ' нежелательный элемент за номером ' + str(perk) +
                         ' сотворил злую шутку, исправь')
        continue
if string != '':
    string = string.rstrip()
    string = string[:-1]
    string += ';'
    db.create_lots(start_string + string)
    string = ''


# ====================================================================================

draw = '<code>' + start_message.text + '\n' + log(0) + '</code>'
try:
    bot.edit_message_text(chat_id=start_message.chat.id, text=draw,
                          message_id=start_message.message_id, parse_mode='HTML')
except:
    draw += '\n<b>Старые посты из таблицы добавлены в бота.\nНе смог отредактировать сообщение.</b>'
    bot.send_message(idMe, draw, parse_mode='HTML')


def executive(name):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error = ''
    for i in error_raw:
        error += str(i)
    bot.send_message(idMe, 'Вылет ' + name + '\n' + error)
    _thread.exit()


def former(text, id, type):
    goo = []
    soup = BeautifulSoup(text.text, 'html.parser')
    is_post_not_exist = str(soup.find('div', class_='tgme_widget_message_error'))
    if str(is_post_not_exist) == str(None):
        stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60
        string = str(soup.find('div', class_='tgme_widget_message_text js-message_text'))
        string = re.sub(' (dir|class|style)=\\"\w+[^\\"]+\\"', '', string)
        string = re.sub('(<b>|</b>|<i>|</i>|<div>|</div>)', '', string)
        string = re.sub('/', '&#47;', string)
        string = re.sub('(<br&#47;>)', '/', string)
        string = str(id) + '/' + string

        if type == 'old':
            drop_time = soup.find('time', class_='datetime')
            stamp = int(
                time.mktime(datetime.strptime(str(drop_time['datetime']), '%Y-%m-%dT%H:%M:%S+00:00').timetuple()))
            if stamp <= stamp_now:
                goo.append(string)
            else:
                goo.append('active')
        else:
            goo = form_mash(string)
    else:
        goo.append('false')
    return goo


def oldest():
    while True:
        try:
            global data1
            global old
            thread_name = 'oldest '
            sleep(1)
            text = requests.get(dim.adress + str(old) + '?embed=1')
            if str(old) not in ignore:
                goo = former(text, old, 'old')
                if goo[0] == 'active':
                    print(thread_name + dim.adress + str(old) + ' Активен, ничего не делаю')
                elif goo[0] == 'false':
                    print(thread_name + dim.adress + str(old) + ' Форму не нашло')
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
                    sleep(4)
                    print(thread_name + dim.adress + str(old) + ' Добавил в google старый лот')
            else:
                print(thread_name + dim.adress + str(old) + ' В черном списке, пропускаю')
                old = old + 1

        except IndexError:
            thread_name = 'oldest'
            executive(thread_name)


def detector():
    while True:
        try:
            global new
            global firstopen
            global data5
            thread_name = 'detector '
            db = SQLighter('old.db')
            db_new = SQLighter('new.db')
            if firstopen == 1:
                creds5 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_active, scope)
                client5 = gspread.authorize(creds5)
                data5 = client5.open(dim.file).worksheet('active')
                google = data5.col_values(1)
                for i in google:
                    if i != '':
                        text = requests.get(dim.adress + i + '?embed=1')
                        sleep(0.01)
                        try:
                            auid_raw = db_new.get_new_auid()
                        except:
                            sleep(2)
                            auid_raw = db_new.get_new_auid()
                        auid = []
                        if str(auid_raw) != 'False':
                            for g in auid_raw:
                                auid.append(g[0])
                        goo = former(text, int(i), 'new')
                        if goo[0] != 'false':
                            if goo[10] == '#active' and int(goo[0]) not in auid:
                                try:
                                    db_new.create_new_lot(goo[0])
                                except:
                                    sleep(2)
                                    db_new.create_new_lot(goo[0])
                firstopen = 0

            text = requests.get(dim.adress + str(new) + '?embed=1')
            sleep(0.3)
            if str(new) not in ignore:
                goo = former(text, new, 'new')
                if goo[0] != 'false':
                    new += 1
                    if goo[10] == '#active':
                        try:
                            auid_raw = db_new.get_new_auid()
                        except:
                            sleep(2)
                            auid_raw = db_new.get_new_auid()
                        auid = []
                        if str(auid_raw) != 'False':
                            for g in auid_raw:
                                auid.append(g[0])
                        if int(goo[0]) not in auid:
                            try:
                                db_new.create_new_lot(goo[0])
                            except:
                                sleep(2)
                                db_new.create_new_lot(goo[0])
                            print(thread_name + dim.adress + str(new) + ' Добавлен в базу активных')
                        else:
                            print(thread_name + dim.adress + str(new) + ' Уже есть в базе активных')
                    else:
                        auid_raw_old = db.get_auid()
                        auid_old = []
                        if str(auid_raw_old) != 'False':
                            for g in auid_raw_old:
                                auid_old.append(g[0])
                        if int(goo[0]) not in auid_old:
                            db.create_lot(goo[0], goo[1], goo[2], goo[3], goo[4], goo[5],
                                          goo[6], goo[7], goo[8], goo[9], goo[10])
                        print(thread_name + dim.adress + str(new) + ' Добавил в базу старых')
                else:
                    print(thread_name + dim.adress + str(new) + ' Форму не нашло')
                    sleep(1)
                    if firstopen == 0:
                        draw = '<code>' + start_message.text + '\n' + log(0) + '</code>'
                        try:
                            bot.edit_message_text(chat_id=start_message.chat.id, text=draw,
                                                  message_id=start_message.message_id, parse_mode='HTML')
                        except:
                            draw += '\n<b>Старые посты не из таблицы добавлены в бота.\n' \
                                    'Не смог отредактировать сообщение.</b>'
                            bot.send_message(idMe, draw, parse_mode='HTML')
                        firstopen -= 1
            else:
                print(thread_name + dim.adress + str(old) + ' В черном списке, пропускаю')

        except IndexError:
            thread_name = 'detector'
            executive(thread_name)


def lot_updater():
    while True:
        try:
            global firstopen
            thread_name = 'lot_updater '
            print(thread_name + 'начало')
            db = SQLighter('old.db')
            db_new = SQLighter('new.db')
            if firstopen == 1:
                sleep(10)
            try:
                auid_raw = db_new.get_new_auid()
            except:
                sleep(2)
                auid_raw = db_new.get_new_auid()
            auid = []
            if str(auid_raw) != 'False':
                for g in auid_raw:
                    auid.append(g[0])
            for i in auid:
                text = requests.get(dim.adress + str(i) + '?embed=1')
                sleep(0.01)
                goo = former(text, int(i), 'new')
                if goo[0] != 'false':
                    if goo[14] != '#active':
                        try:
                            db_new.delete_new_lot(goo[0])
                        except:
                            sleep(2)
                            db_new.delete_new_lot(goo[0])
                        auid_raw_old = db.get_auid()
                        auid_old = []
                        if str(auid_raw_old) != 'False':
                            for g in auid_raw_old:
                                auid_old.append(g[0])
                        if int(goo[0]) not in auid_old:
                            db.create_lot(goo[0], goo[1], goo[2], goo[3], goo[4], goo[5],
                                          goo[6], goo[7], goo[8], goo[9], goo[10])
            print(thread_name + ' удалил закончившиеся из базы')
            sleep(3)
        except IndexError:
            thread_name = 'lot_updater'
            executive(thread_name)


def google_updater():
    while True:
        try:
            global firstopen
            global data5
            thread_name = 'google_updater '
            print(thread_name + 'начало')
            db_new = SQLighter('new.db')
            if firstopen == 1:
                sleep(10)
            if firstopen != 1:
                try:
                    google = data5.col_values(1)
                except:
                    creds5 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_active, scope)
                    client5 = gspread.authorize(creds5)
                    data5 = client5.open(dim.file).worksheet('active')
                    google = data5.col_values(1)
                sleep(2)
                try:
                    auid_raw = db_new.get_new_auid()
                except:
                    sleep(2)
                    auid_raw = db_new.get_new_auid()
                auid = []
                if str(auid_raw) != 'False':
                    for g in auid_raw:
                        auid.append(g[0])
                for i in auid:
                    if str(i) not in google:
                        try:
                            data5.insert_row([int(i)], 1)
                        except:
                            creds5 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_active, scope)
                            client5 = gspread.authorize(creds5)
                            data5 = client5.open(dim.file).worksheet('active')
                            data5.insert_row([int(i)], 1)
                        sleep(2)
                print(thread_name + ' добавил новые лоты в google')

                try:
                    google = data5.col_values(1)
                except:
                    creds5 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_active, scope)
                    client5 = gspread.authorize(creds5)
                    data5 = client5.open(dim.file).worksheet('active')
                    google = data5.col_values(1)
                sleep(2)
                try:
                    auid_raw = db_new.get_new_auid()
                except:
                    sleep(2)
                    auid_raw = db_new.get_new_auid()
                auid = []
                if str(auid_raw) != 'False':
                    for g in auid_raw:
                        auid.append(g[0])
                count = 1
                for i in google:
                    if i != '':
                        if int(i) not in auid:
                            try:
                                data5.delete_row(google.index(i) + count)
                            except:
                                creds5 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_active, scope)
                                client5 = gspread.authorize(creds5)
                                data5 = client5.open(dim.file).worksheet('active')
                                data5.delete_row(google.index(i) + count)
                            sleep(2)
                            count -= 1
                print(thread_name + ' удалил закончившиеся из google')
        except IndexError:
            thread_name = 'google_updater'
            executive(thread_name)


def messages():
    while True:
        try:
            global i
            thread_name = 'messages '
            print(thread_name + 'начало')
            db = SQLighter('old.db')
            creds2 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_storage, scope)
            creds3 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_storage_supp, scope)
            client2 = gspread.authorize(creds2)
            client3 = gspread.authorize(creds3)
            data2 = client2.open('Info').worksheet('const_uber')
            data3 = client3.open(dim.file).worksheet('storage')
            const_pre = data2.col_values(2)
            sleep(1)
            data2 = client2.open(dim.file).worksheet('storage')
            const = []
            const2 = []
            for g in const_pre:
                const.append(g + '/none')
                qualities_raw = db.get_quality(g)
                if str(qualities_raw) != 'False':
                    qualities = []
                    for f in qualities_raw:
                        splited = f[0]
                        splited = splited.split('.')
                        if splited[0] not in qualities:
                            qualities.append(splited[0])
                    for f in qualities:
                        if f != 'none':
                            const2.append(g + '/' + f)
            for g in const2:
                const.append(g)
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
                splited = const[i].split('/')
                col = db.get_lots(splited[0])
                if str(col) != 'False':
                    for z in col:
                        qua = z[4].split('.')
                        quality = qua[0]
                        cost = z[7]
                        buyer = z[8]
                        stamp = z[9]
                        status = z[10]
                        if status != 'Cancelled' and quality == splited[1]:
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
                        lastsold = dim.lastsold + str(last)
                    else:
                        lastsold = ''
                        last = 0

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
                    last = 0

                if f_min == 1000:
                    f_min = 0
                if min_30 == 1000:
                    min_30 = 0

                print(thread_name + 'i = ' + str(i) + ' last = ' + str(last))
                text = text + dim.soldtimes + str(len(newcol)) + '\n\n' + \
                    dim.alltime + \
                    dim.median + str(median) + '\n' + \
                    dim.average + str(f_average) + '\n' + \
                    dim.minmax + str(f_min) + '/' + str(f_max) + '\n' + \
                    dim.unsold + str(f_un_average) + '/' + str(len(newcol) + f_un_average) + '\n\n' + \
                    dim.days + \
                    dim.median + str(median_30) + '\n' + \
                    dim.average + str(average_30) + '\n' + \
                    dim.minmax + str(min_30) + '/' + str(max_30) + '\n' + \
                    dim.unsold + str(un_average_30) + '/' + str(len(newcol_30) + un_average_30) + \
                    str(lastsold) + '\n\n'

                try:
                    data2.update_cell(1, i + 1, const[i])
                    data3.update_cell(2, i + 1, text)
                except:
                    creds2 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_storage, scope)
                    creds3 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_storage_supp, scope)
                    client2 = gspread.authorize(creds2)
                    client3 = gspread.authorize(creds3)
                    data2 = client2.open(dim.file).worksheet('storage')
                    data3 = client3.open(dim.file).worksheet('storage')
                    data2.update_cell(1, i + 1, const[i])
                    data3.update_cell(2, i + 1, text)
                sleep(1)
                i = i + 1
            print(thread_name + 'конец')
        except IndexError:
            thread_name = 'messages'
            executive(thread_name)


def checker():
    while True:
        try:
            sleep(10)
            global data1
            global old
            thread_name = 'checker '
            print(thread_name + 'начало')
            check = copy.copy(old)
            try:
                google = data1.col_values(1)
            except:
                creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
                client1 = gspread.authorize(creds1)
                data1 = client1.open(dim.file).worksheet('old')
                google = data1.col_values(1)
            check -= 1000
            while check < int(google[1]):
                sleep(2)
                text = requests.get(dim.adress + str(check) + '?embed=1')
                print(thread_name + 'проверяю наличие ' + dim.adress + str(check))
                if str(check) not in ignore:
                    goo = former(text, check, 'old')
                    if goo[0] == 'active':
                        bot.send_message(idMe, '🧐\n' + dim.adress + str(check) +
                                         '\n\n' + str(goo[0]) + '\n\nЧто-то странненькое')
                    elif goo[0] not in google:
                        bot.send_message(idMe, '🤔\n' + dim.adress + str(check) +
                                         '\n\n' + str(goo[0]) + '\n\nЭтого лота нет в базе, проверь')
                else:
                    print(thread_name + dim.adress + str(check) + ' В черном списке, пропускаю')
                check += 1
            print(thread_name + 'конец')
        except IndexError:
            thread_name = 'checker'
            executive(thread_name)


def double_checker():
    while True:
        try:
            sleep(1800)
            thread_name = 'double_checker '
            print(thread_name + 'начало')
            global data1
            try:
                google = data1.col_values(1)
            except:
                creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
                client1 = gspread.authorize(creds1)
                data1 = client1.open(dim.file).worksheet('old')
                google = data1.col_values(1)
            for i in google:
                if google.count(i) > 1:
                    bot.send_message(idMe, 'Элемент\n\n' + str(i) + '\n\nповторяется в базе '
                                     + str(google.count(i)) + ' раз.\nНа данный момент он находится на позиции '
                                     + str(google.index(i)) + ' в массиве')
            print(thread_name + 'конец')
            sleep(10800)
        except IndexError:
            thread_name = 'double_checker'
            executive(thread_name)


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    if message.chat.id != idMe:
        bot.send_message(message.chat.id, 'К тебе этот бот не имеет отношения, уйди пожалуйста')
    else:
        if message.text == '/base':
            doc_new = open('new.db', 'rb')
            doc_old = open('old.db', 'rb')
            bot.send_document(idMe, doc_new)
            bot.send_document(idMe, doc_old)
        else:
            bot.send_message(message.chat.id, 'Я работаю')


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    _thread.start_new_thread(oldest, ())
    _thread.start_new_thread(detector, ())
    _thread.start_new_thread(lot_updater, ())
    _thread.start_new_thread(google_updater, ())
    # _thread.start_new_thread(messages, ())
    _thread.start_new_thread(checker, ())
    _thread.start_new_thread(double_checker, ())
    telepol()

