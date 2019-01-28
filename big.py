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

ignore = str(google[0])
old = int(google[1])
new = copy.copy(old)
check = copy.copy(old)
firstopen = 1
ignore = ignore.split('/')


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


def oldest():
    while True:
        try:
            global data1
            global old
            thread_name = 'oldest '
            sleep(3)
            text = requests.get(dim.adress + str(old))
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
                    print(thread_name + dim.adress + str(old) + ' Добавил в google старый лот')
            else:
                print(thread_name + dim.adress + str(old) + ' В черном списке, пропускаю')
                old = old + 1

        except Exception as e:
            thread_name = 'oldest '
            bot.send_message(idMe, 'вылет ' + thread_name + '\n' + str(e))
            sleep(1)


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
                        text = requests.get(dim.adress + i)
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
                        row = goo[0].split('/')
                        if row[0] != 'false':
                            if row[14] == '#active' and int(row[0]) not in auid:
                                try:
                                    db_new.create_new_lot(row[0])
                                except:
                                    sleep(2)
                                    db_new.create_new_lot(row[0])
                firstopen = 0

            text = requests.get(dim.adress + str(new))
            sleep(0.01)
            if str(new) not in ignore:
                goo = former(text, new, 'new')
                row = goo[0].split('/')
                if row[0] != 'false':
                    new += 1
                    if row[14] == '#active':
                        try:
                            auid_raw = db_new.get_new_auid()
                        except:
                            sleep(2)
                            auid_raw = db_new.get_new_auid()
                        auid = []
                        if str(auid_raw) != 'False':
                            for g in auid_raw:
                                auid.append(g[0])
                        if int(row[0]) not in auid:
                            try:
                                db_new.create_new_lot(row[0])
                            except:
                                sleep(2)
                                db_new.create_new_lot(row[0])
                            print(thread_name + dim.adress + str(new) + ' Добавлен в базу активных')
                        else:
                            print(thread_name + dim.adress + str(new) + ' Уже есть в базе активных')
                    else:
                        auid_raw_old = db.get_auid()
                        auid_old = []
                        if str(auid_raw_old) != 'False':
                            for g in auid_raw_old:
                                auid_old.append(g[0])
                        if int(row[0]) not in auid_old:
                            stamp = timer([row[9], row[10], row[11], row[12], row[13]])
                            db.create_lot(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], stamp,
                                          row[14])
                        print(thread_name + dim.adress + str(new) + ' Добавил в базу старых')
                else:
                    print(thread_name + dim.adress + str(new) + ' Форму не нашло')
                    sleep(1)
                    if firstopen == 0:
                        print(log(0))
                        firstopen -= 1
            else:
                print(thread_name + dim.adress + str(old) + ' В черном списке, пропускаю')

        except Exception as e:
            thread_name = 'detector '
            bot.send_message(idMe, 'вылет ' + thread_name + '\n' + str(e))
            sleep(1)


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
                text = requests.get(dim.adress + str(i))
                sleep(0.01)
                goo = former(text, int(i), 'new')
                row = goo[0].split('/')
                if row[0] != 'false':
                    if row[14] != '#active':
                        try:
                            db_new.delete_new_lot(row[0])
                        except:
                            sleep(2)
                            db_new.delete_new_lot(row[0])
                        auid_raw_old = db.get_auid()
                        auid_old = []
                        if str(auid_raw_old) != 'False':
                            for g in auid_raw_old:
                                auid_old.append(g[0])
                        if int(row[0]) not in auid_old:
                            stamp = timer([row[9], row[10], row[11], row[12], row[13]])
                            db.create_lot(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                          row[8], stamp, row[14])
            print(thread_name + ' удалил закончившиеся из базы')
            sleep(3)

        except Exception as e:
            thread_name = 'lot_updater '
            bot.send_message(idMe, 'вылет ' + thread_name + '\n' + str(e))
            sleep(1)


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
                    sleep(1)
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
                        sleep(1)
                        count -= 1
            print(thread_name + ' удалил закончившиеся из google')

        except Exception as e:
            thread_name = 'google_updater '
            bot.send_message(idMe, 'вылет ' + thread_name + '\n' + str(e))
            sleep(1)


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
            data2 = client2.open('Active-Info').worksheet('const')
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
                        qualities.append(f[0])
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
                        quality = z[4]
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
        except Exception as e:
            thread_name = 'messages '
            bot.send_message(idMe, 'вылет ' + thread_name + ': i = ' + str(i) + '\n' + str(e))
            sleep(1)


def checker():
    while True:
        try:
            sleep(10)
            global data1
            global old
            global check
            thread_name = 'checker '
            print(thread_name + 'начало')
            try:
                google = data1.col_values(1)
            except:
                creds1 = ServiceAccountCredentials.from_json_keyfile_name(dim.json_old, scope)
                client1 = gspread.authorize(creds1)
                data1 = client1.open(dim.file).worksheet('old')
                google = data1.col_values(1)
            check -= 1000
            while check < old:
                sleep(2)
                text = requests.get(dim.adress + str(check))
                print(thread_name + 'проверяю наличие ' + dim.adress + str(check))
                if str(check) not in ignore:
                    goo = former(text, check, 'old')
                    if goo[0] == 'active' or goo[0] == 'false':
                        bot.send_message(idMe, '🧐\n' + dim.adress + str(check) +
                                         '\n\n' + str(goo[0]) + '\n\nЧто-то странненькое')
                    elif goo[0] not in google:
                        bot.send_message(idMe, '🤔\n' + dim.adress + str(check) +
                                         '\n\n' + str(goo[0]) + '\n\nЭтого лота нет в базе, проверь')
                else:
                    print(thread_name + dim.adress + str(check) + ' В черном списке, пропускаю')
                check += 1
            print(thread_name + 'конец')
        except Exception as e:
            thread_name = 'checker '
            bot.send_message(idMe, 'вылет ' + thread_name + '\n' + str(e))
            sleep(1)


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
        except Exception as e:
            thread_name = 'double_checker '
            bot.send_message(idMe, 'вылет ' + thread_name + '\n' + str(e))
            sleep(1)


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    if message.chat.id != idMe:
        bot.send_message(message.chat.id, 'К тебе этот бот не имеет отношения, уйди пожалуйста')
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
    _thread.start_new_thread(messages, ())
    _thread.start_new_thread(checker, ())
    _thread.start_new_thread(double_checker, ())
    telepol()
