# -*- coding: utf-8 -*-
import re
import copy
import _thread
import gspread
import requests
import datetime
import dimensional
from time import sleep
from SQL import SQLighter
from bs4 import BeautifulSoup
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

from additional.objects import bold
from additional.objects import code
from additional.objects import start_main_bot
from additional.objects import start_message
from additional.objects import log_time
from additional.objects import printer
from additional.objects import query
from additional.objects import italic
from additional.objects import properties_json
from additional.objects import stamper
from additional.objects import send_dev_message
from additional.objects import edit_dev_message
from additional.objects import thread_exec as executive
from game_time import timer

stamp1 = int(datetime.now().timestamp())
server = dimensional.server
variable = dimensional.res
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
start_sql_request = 'INSERT INTO old (au_id, lot_id, enchant, item_name, quality, ' \
                    'condition, modifiers, seller, cost, buyer, stamp, status) VALUES '
properties_title_list = ['lot_id', 'enchant', 'item_name', 'quality', 'condition',
                         'modifiers', 'seller', 'cost', 'buyer', 'stamp', 'status', 'raw']
lot_updater_channel = 'https://t.me/lot_updater/'
idMe = 396978030
old_values = []
first_open = 1
limit = 50000
old = 0
# ====================================================================================


def form_mash(lot):
    stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60
    lot = re.sub('\'', '&#39;', lot)
    lot_properties = {'au_id': 0}
    lot_split = lot.split('/')
    search_au_id = re.search('(\d+)', lot_split[0])
    if search_au_id:
        lot_properties['au_id'] = int(search_au_id.group(1))
    for i in properties_title_list:
        if i == 'lot_id' or i == 'stamp':
            lot_properties[i] = 0
        else:
            lot_properties[i] = 'None'
    for g in lot_split:
        for i in variable['form'][server]:
            search = re.search(variable['form'][server].get(i), g)
            if search:
                if i == 'title':
                    item_name = re.sub(' \+\d+[⚔🛡]', '', search.group(2))
                    enchant_search = re.search('⚡\+(\d+) ', item_name)
                    lot_properties['lot_id'] = int(search.group(1))
                    item_name = re.sub(' \+\d+💧', '', item_name)
                    enchant = 'None'
                    if enchant_search:
                        item_name = re.sub('⚡\+\d+ ', '', item_name)
                        enchant = enchant_search.group(1)
                    lot_properties['item_name'] = item_name
                    lot_properties['enchant'] = enchant
                elif i == 'condition':
                    lot_properties[i] = re.sub(' ⏰.*', '', search.group(1))
                elif i == 'modifiers':
                    lot_properties[i] = ''
                elif i == 'cost':
                    lot_properties[i] = int(search.group(1))
                elif i == 'stamp':
                    lot_properties[i] = timer(search)
                elif i == 'status':
                    status = search.group(1)
                    if status == 'Failed':
                        status = 'Cancelled'
                    if status == '#active':
                        if lot_properties['stamp'] < stamp_now:
                            status = 'Finished'
                    lot_properties[i] = status
                elif i == 'raw':
                    lot_properties[i] = lot
                else:
                    lot_properties[i] = search.group(1)
        if lot_properties['modifiers'] != 'None' and g.startswith(' '):
            lot_properties['modifiers'] += '  ' + g.strip() + '\n'
    if lot_properties['modifiers'] != 'None' and lot_properties['modifiers'].endswith('\n'):
        lot_properties['modifiers'] = lot_properties['modifiers'][:-1]
    return lot_properties


def database_filler():
    global old
    global old_values
    global creds1
    global client1
    global worksheet
    db = SQLighter('old.db')
    creds1 = ServiceAccountCredentials.from_json_keyfile_name(variable['json_old'][server], scope)
    client1 = gspread.authorize(creds1)
    spreadsheet_list = client1.list_spreadsheet_files()
    for s in spreadsheet_list:
        document_name = s['name']
        if document_name == variable['document'][server] or document_name == 'temp-' + variable['document'][server]:
            document = client1.open(document_name)
            for w in document.worksheets():
                worksheet = document.worksheet(w.title)
                values = worksheet.col_values(1)
                sql_request_line = ''
                position = 0
                point = 0
                if w.title == 'old':
                    old_values = values
                for g in values:
                    position += 1
                    lot_object = form_mash(g)
                    au_id = lot_object.get('au_id')
                    if au_id > old:
                        old = au_id
                    if au_id != 0:
                        sql_request_line += "('{}', '{}', '{}', '{}', '{}', '{}', " \
                                            "'{}', '{}', '{}', '{}', '{}', '{}'), ".format(*lot_object.values())
                        point += 1
                        if point == 1000:
                            sql_request_line = sql_request_line.rstrip()
                            sql_request_line = sql_request_line[:-1] + ';'
                            db.create_lots(start_sql_request + sql_request_line)
                            sql_request_line = ''
                            point = 0
                    else:
                        error = document_name + '/' + w.title + '/' + str(position) + ' пуст или неисправен'
                        send_dev_message(variable['document'][server], error)
                if sql_request_line != '':
                    sql_request_line = sql_request_line.rstrip()
                    sql_request_line = sql_request_line[:-1] + ';'
                    db.create_lots(start_sql_request + sql_request_line)
    double = []
    double_raw = db.get_double()
    if double_raw:
        for i in double_raw:
            lot_header = str(i[0]) + '/' + variable['lot'][server] + str(i[1])
            if lot_header not in double:
                double.append(lot_header)
    for lot_header in double:
        send_dev_message(variable['document'][server], 'Повторяющийся в базе элемент: ' + bold(lot_header))
    worksheet = client1.open('temp-' + variable['document'][server]).worksheet('old')
    old_values = worksheet.col_values(1)


start_search = query(lot_updater_channel + str(variable['lots_post_id'][server]), '(.*)')
if start_search:
    s_message = start_message(variable['document'][server], stamp1)
    database_filler()
    s_message = edit_dev_message(s_message, '\n' + log_time(tag=code))
else:
    additional_text = '\nНет подключения к ' + lot_updater_channel + bold('Бот выключен')
    s_message = start_message(variable['file'][server], stamp1, additional_text)
    _thread.exit()
bot = start_main_bot('non-async', variable['TOKEN'][server])
new = copy.copy(old + 1)
old += 1
# ====================================================================================


def editor(text, print_text):
    try:
        bot.edit_message_text(code(text), -1001376067490, variable['lots_post_id'][server], parse_mode='HTML')
    except IndexError and Exception:
        print_text += ' (пост не изменился)'
    printer(print_text)


def google(action, option=None):
    global creds1
    global client1
    global worksheet
    global old_values
    if action == 'old_insert':
        try:
            worksheet.update_cell(len(old_values) + 1, 1, option)
        except IndexError and Exception as error:
            search_exceed = re.search('exceeds grid limits', str(error))
            if search_exceed:
                sleep(60)
                worksheet_number = 0
                storage_name = variable['document'][server]
                dev = send_dev_message('temp-' + storage_name, 'Устраняем таблицу', tag=italic, good=True)
                creds1 = ServiceAccountCredentials.from_json_keyfile_name(variable['json_old'][server], scope)
                client1 = gspread.authorize(creds1)
                temp_document = client1.open('temp-' + storage_name)
                temp_worksheet = temp_document.worksheet('old')
                values = temp_worksheet.col_values(1)
                document = client1.open(storage_name)
                for i in document.worksheets():
                    if int(i.title) > worksheet_number:
                        worksheet_number = int(i.title)
                worksheet = document.add_worksheet(str(worksheet_number + 1), limit, 1)
                worksheet.format('A1:A' + str(limit), {'horizontalAlignment': 'CENTER'})
                document.batch_update(properties_json(worksheet.id))
                cell_list = worksheet.range('A1:A' + str(limit))
                dev = edit_dev_message(dev, italic('\n— Новая: ' + storage_name + '/' + str(worksheet_number + 1)))
                for g in range(0, len(values)):
                    cell_list[g].value = values[g]
                worksheet.update_cells(cell_list)
                document = client1.create('temp-' + storage_name)
                for i in variable['emails'][server]:
                    document.share(i, 'user', 'writer', False)
                worksheet = document.add_worksheet(title='old', rows=limit, cols=1)
                worksheet.format('A1:A' + str(limit), {'horizontalAlignment': 'CENTER'})
                document.batch_update(properties_json(worksheet.id))
                document.del_worksheet(document.worksheet('Sheet1'))
                client1.del_spreadsheet(temp_document.id)
                worksheet.update_cell(1, 1, option)
                edit_dev_message(dev, italic('\n— Успешно'))
                old_values = []
                sleep(30)
            else:
                creds1 = ServiceAccountCredentials.from_json_keyfile_name(variable['json_old'][server], scope)
                client1 = gspread.authorize(creds1)
                worksheet = client1.open('temp-' + variable['document'][server]).worksheet('old')
                worksheet.update_cell(len(old_values) + 1, 1, option)


def updater(pos, cost, stat, const):
    global data2
    row = str(pos + 1)
    try:
        cell_list = data2.range('A' + row + ':C' + row)
        cell_list[0].value = const[pos]
        cell_list[1].value = cost
        cell_list[2].value = stat
        data2.update_cells(cell_list)
    except IndexError and Exception:
        creds2 = ServiceAccountCredentials.from_json_keyfile_name(variable['json_storage'][server], scope)
        client2 = gspread.authorize(creds2)
        data2 = client2.open('Notify').worksheet(variable['zone'][server] + 'storage')
        cell_list = data2.range('A' + row + ':C' + row)
        cell_list[0].value = const[pos]
        cell_list[1].value = cost
        cell_list[2].value = stat
        data2.update_cells(cell_list)
    sleep(1)
    printer('i = ' + str(pos) + ' новое')


def former(text, form='new'):
    soup = BeautifulSoup(text.text, 'html.parser')
    is_post_not_exist = soup.find('div', class_='tgme_widget_message_error')
    if is_post_not_exist is None:
        stamp_day_ago = int(datetime.now().timestamp()) - 24 * 60 * 60
        lot_raw = str(soup.find('div', class_='tgme_widget_message_text js-message_text')).replace('<br/>', '\n')
        au_id = re.sub('t.me/.*?/', '', soup.find('div', class_='tgme_widget_message_link').get_text())
        lot = BeautifulSoup(lot_raw, 'html.parser').get_text()
        response = {'raw': au_id + '/' + re.sub('/', '&#47;', lot).replace('\n', '/')}
        if form == 'new':
            response = form_mash(response['raw'])
        else:
            drop_time = soup.find('time', class_='datetime')
            stamp = stamper(str(drop_time['datetime']), '%Y-%m-%dT%H:%M:%S+00:00')
            if stamp > stamp_day_ago:
                response = {'raw': 'active'}
    else:
        response = {'raw': 'False'}
    return response


def oldest():
    while True:
        try:
            global old
            print_text = variable['destination'][server] + str(old)
            text = requests.get(print_text + '?embed=1')
            response = former(text, 'old')
            if response['raw'] == 'active':
                print_text += ' Активен, ничего не делаю'
                sleep(7)
            elif response['raw'] == 'False':
                print_text += ' Форму не нашло'
                sleep(1)
            else:
                old = old + 1
                google('old_insert', response['raw'])
                old_values.append(response['raw'])
                sleep(1)
                print_text += ' Добавил в google старый лот'
            printer(print_text)
        except IndexError and Exception:
            executive()


def detector():
    while True:
        try:
            global new
            global first_open
            db = SQLighter('old.db')
            db_new = SQLighter('new.db')
            if first_open == 1:
                lots_raw = query(lot_updater_channel + str(variable['lots_post_id'][server]), '(.*)')
                if lots_raw:
                    a_lots = lots_raw.group(1).split('/')
                    for i in a_lots:
                        if i != '':
                            text = requests.get(variable['destination'][server] + i + '?embed=1')
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
                            goo = former(text)
                            if goo[0] != 'False':
                                if goo[10] == '#active' and int(goo[0]) not in auid:
                                    try:
                                        db_new.create_new_lot(goo[0])
                                    except:
                                        sleep(2)
                                        db_new.create_new_lot(goo[0])
                    first_open = 0

            sleep(0.3)
            print_text = variable['destination'][server] + str(new)
            text = requests.get(print_text + '?embed=1')
            goo = former(text)
            if goo[0] != 'False':
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
                        print_text += ' Добавлен в базу активных'
                    else:
                        print_text += ' Уже есть в базе активных'
                else:
                    auid_raw_old = db.get_auid()
                    auid_old = []
                    if str(auid_raw_old) != 'False':
                        for g in auid_raw_old:
                            auid_old.append(g[0])
                    if int(goo[0]) not in auid_old:
                        db.create_lot(goo[0], goo[1], goo[2], goo[3], goo[4], goo[5],
                                      goo[6], goo[7], goo[8], goo[9], goo[10])
                    print_text += ' Добавил в базу старых'
                new += 1
            else:
                print_text += ' Форму не нашло'
                sleep(8)
                if first_open == 0:
                    edit_dev_message(s_message, '\n' + log_time(tag=code))
                    first_open -= 1
            printer(print_text)
        except IndexError and Exception:
            executive()


def lot_updater():
    while True:
        try:
            global first_open
            if first_open == 1:
                sleep(10)
            printer('начало')
            db = SQLighter('old.db')
            db_new = SQLighter('new.db')
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
                text = requests.get(variable['destination'][server] + str(i) + '?embed=1')
                sleep(5)
                goo = former(text)
                if goo[0] != 'False':
                    if goo[10] != '#active':
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
            printer('удалил закончившиеся из базы')
            sleep(5)
        except IndexError and Exception:
            executive()


def telegram():
    while True:
        try:
            global first_open
            db_new = SQLighter('new.db')
            if first_open == 1:
                sleep(10)
            if first_open != 1:
                sleep(20)
                printer('начало')
                lots_raw = query(lot_updater_channel + str(variable['lots_post_id'][server]), '(.*)')
                if lots_raw:
                    array = lots_raw.group(1).split('/')
                    row = '/'
                    for i in array:
                        if i != '':
                            row += i + '/'
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
                        if str(i) not in array:
                            if len(row) < 4085:
                                row += str(i) + '/'
                    if row == '/':
                        row = 'None'

                    editor(row, 'добавил новые лоты в telegram')

                    if row != 'None':
                        array = row.split('/')
                    else:
                        array = []
                    try:
                        auid_raw = db_new.get_new_auid()
                    except:
                        sleep(2)
                        auid_raw = db_new.get_new_auid()
                    auid = []
                    if str(auid_raw) != 'False':
                        for g in auid_raw:
                            auid.append(g[0])
                    for i in array:
                        if i != '':
                            if int(i) not in auid:
                                row = re.sub('/' + str(i) + '/', '/', row)
                    if row == '/':
                        row = 'None'
                    editor(row, 'удалил закончившиеся из google')
        except IndexError and Exception:
            executive()


def messages():
    while True:
        try:
            if first_open == -1:
                global data2
                printer('начало')
                db = SQLighter('old.db')
                creds2 = ServiceAccountCredentials.from_json_keyfile_name(variable['json_storage'][server], scope)
                client2 = gspread.authorize(creds2)
                data2 = client2.open('Notify').worksheet('const_items')
                const_pre = data2.col_values(2)
                data2 = client2.open('Notify').worksheet(variable['zone'][server] + 'storage')
                google = data2.col_values(3)
                sleep(2)
                const = []
                for g in const_pre:
                    const.append(g + '/none')
                    qualities_raw = db.get_quality(g)
                    if str(qualities_raw) != 'False':
                        qualities = []
                        for f in qualities_raw:
                            splited = f[0].split('.')
                            if splited[0] not in qualities:
                                qualities.append(splited[0])
                        if len(qualities) > 1:
                            const.append(g + '/Common')
                        for f in qualities:
                            if f != 'none':
                                const.append(g + '/' + f)
                i = 0
                while i < len(const):
                    text = ''
                    time_30 = int(datetime.now().timestamp()) - (7 * 24 * 60 * 60)
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
                            if status != 'Cancelled':
                                if quality == splited[1] or splited[1] == 'none' or \
                                        (splited[1] == 'Common' and quality == 'none'):
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
                            lastsold = '_{8} ' + str(last)
                        else:
                            lastsold = ''

                        newcol.sort()
                        newcol_30.sort()

                        if len(newcol) % 2 == 0 and len(newcol) != 0:
                            lot1 = int(newcol[len(newcol) // 2])
                            lot2 = int(newcol[len(newcol) // 2 - 1])
                            median = round((lot1 + lot2) / 2, 2)
                            if (median % int(median)) == 0:
                                median = int(median)
                        elif len(newcol) == 0:
                            median = 0
                        else:
                            median = int(newcol[len(newcol) // 2])

                        if len(newcol_30) % 2 == 0 and len(newcol_30) != 0:
                            lot1_30 = int(newcol_30[len(newcol_30) // 2])
                            lot2_30 = int(newcol_30[len(newcol_30) // 2 - 1])
                            median_30 = round((lot1_30 + lot2_30) / 2, 2)
                            if (median_30 % int(median_30)) == 0:
                                median_30 = int(median_30)
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

                    t_costs = str(median) + '/' + str(median_30)

                    text += '__' + bold('{1} ') + str(len(newcol)) + '__' + \
                        bold('{2}') + '_' + \
                        '{4} ' + str(median) + '_' + \
                        '{5} ' + str(f_average) + '_' + \
                        '{6} ' + str(f_min) + '/' + str(f_max) + '_' + \
                        '{7} ' + str(f_un_average) + '/' + str(len(newcol) + f_un_average) + '__' + \
                        bold('{3}') + '_' + \
                        '{4} ' + str(median_30) + '_' + \
                        '{5} ' + str(average_30) + '_' + \
                        '{6} ' + str(min_30) + '/' + str(max_30) + '_' + \
                        '{7} ' + str(un_average_30) + '/' + str(len(newcol_30) + un_average_30) + \
                        str(lastsold) + '__'

                    if len(google) > i:
                        if text != google[i]:
                            updater(i, t_costs, text, const)
                    else:
                        updater(i, t_costs, text, const)
                    i += 1
                printer('конец')
            else:
                sleep(20)
        except IndexError and Exception:
            executive()


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    if message.chat.id != idMe:
        bot.send_message(message.chat.id, 'К тебе этот бот не имеет отношения, уйди пожалуйста')
    else:
        if message.text.startswith('/base'):
            modified = re.sub('/base_', '', message.text)
            if modified.startswith('n'):
                doc = open('new.db', 'rb')
                bot.send_document(idMe, doc)
            elif modified.startswith('o'):
                doc = open('old.db', 'rb')
                bot.send_document(idMe, doc)
            else:
                doc = open('log.txt', 'rt')
                bot.send_document(idMe, doc)
            doc.close()
        else:
            bot.send_message(message.chat.id, 'Я работаю')


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    gain = [oldest]
    for thread_element in gain:
        _thread.start_new_thread(thread_element, ())
    telepol()
