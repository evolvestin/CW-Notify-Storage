# -*- coding: utf-8 -*-
import os
import re
import codecs
import gspread
import _thread
from copy import copy
from time import sleep
from aiogram import types
from SQL import SQLighter
from statistics import mean
from ast import literal_eval
from aiogram.utils import executor
from additional.GDrive import Drive
from aiogram.dispatcher import Dispatcher
from statistics import median as median_function
from additional.objects import async_exec as executive
from additional.objects import thread_exec as thread_executive
from additional.game_objects import Mash, path, allowed_params_engrave
from additional.objects import code, bold, query, printer, log_time, time_now, concurrent_functions
from additional.objects import secure_sql, append_values, start_message, start_main_bot, edit_dev_message
stamp1 = time_now()

old2 = 0
server = {}
const_base = {}
idMe = 396978030
global_limit = 300
storage_start = True
clear_stats = {'costs_list_full': [], 'costs_list_week': [],
               'unsold_count_full': 0, 'unsold_count_week': 0,
               'cancelled_count_full': 0, 'cancelled_count_week': 0}
# ====================================================================================


def starting_new_lot():
    global old2
    while server.get('link: new_lot_id') is None:
        pass
    new_lot_id_search = query(server['link: new_lot_id'], '(\d+?)/')
    if new_lot_id_search:
        old2 = int(new_lot_id_search.group(1)) + 1
    return 'Переменная old2 = ' + str(old2) + ' загружена'


def starting_const_creation():
    global const_base
    const_emoji = ''
    const_items = spreadsheet.worksheet('items').get('A1:B50000', major_dimension='ROWS')
    for item in const_items:
        item_name = re.sub('️', '', item[0])
        emoji = re.sub(server['non_emoji_symbols'], '', item_name)
        const_base[item_name] = item[1]
        if emoji not in const_emoji and len(emoji) > 0:
            const_emoji += emoji
    server['non_emoji_symbols'] = server['non_emoji_symbols'].format(const_emoji, '{}')
    return 'Константы успешно загружены'


def create_server_json_list():
    global server
    _server_id = 'cw2'
    if os.environ.get('server'):
        _server_id = os.environ['server']
    json_folder_name = 'server_json_' + re.sub('[^\d]', '', _server_id)
    for file_name in os.listdir(json_folder_name):
        search_json = re.search('(\d)\.json', file_name)
        if search_json:
            server['json' + search_json.group(1)] = json_folder_name + '/' + file_name
    server['non_emoji_symbols'] = r"[-0-9a-zA-Zа-яА-ЯёЁ\s_{}!#$%&='@?*\[\]+.^{}()`⚡|~:;/\\]"
    _client = gspread.service_account(server['json2'])
    _spreadsheet = _client.open('Notify')
    return _client, _server_id, _spreadsheet


def starting_active_db_creation():
    global server
    client = Drive(server['json2'])
    files = client.files()
    folder_id = 'None'
    while server.get('storage') is None:
        pass
    for file in files:
        if server['storage'] + '_folder' == file['name']:
            folder_id = file['id']
            break
    for file in files:
        if file.get('parents') and folder_id == file['parents'][0]:
            if file['name'] == re.sub('(.*)/', '', path['lots']):
                server['lots'] = [file['id'], path['lots']]
            if file['name'] == re.sub('(.*)/', '', path['storage']):
                server['storage_file'] = [file['id'], path['storage']]
            if file['name'] == re.sub('(.*)/', '', path['active']):
                server['active'] = [file['id'], path['active']]
                client.download_file(*server['active'])
    return path['active'] + ' загружен'


def starting_server_creation():
    resources = spreadsheet.worksheet('resources').get('A1:Z50000', major_dimension='COLUMNS')
    options = resources.pop(0)
    for option in options:
        for resource in resources:
            if resource[0] == server_id and option != 'options':
                value = resource[options.index(option)]
                if option == 'DATA_TOKEN':
                    server['TOKEN'] = value
                elif option in ['castle_list', 'storage']:
                    server[option] = value
                elif option == 'form':
                    server[option] = literal_eval(re.sub('️', '', value))
                elif option == 'channel':
                    server['link: ' + option] = 'https://t.me/' + value + '/'
                elif option == 'new_lot_id':
                    server['link: ' + option] = 'https://t.me/lot_updater/' + value
                    server[option] = int(value)
                elif option == 'active_lot_ids':
                    server['lot_updater'] = int(value)
    if os.environ.get('server') is None:
        server['TOKEN'] = '429683355:AAF3GReDyewByK-WRLQ44xpCNKIsYg1G8X0'
        server['lot_updater'] = 62
    return 'Серверная константа загружена'


client1, server_id, spreadsheet = create_server_json_list()
functions = [starting_const_creation, starting_server_creation]
concurrent_functions(append_values(functions, [starting_active_db_creation, starting_new_lot]))
bot = start_main_bot('async', server['TOKEN'])
Mash = Mash(server, const_base)
dispatcher = Dispatcher(bot)
# ====================================================================================
s_message = start_message(server['TOKEN'], stamp1)


def drive_updater(drive_client, args, json_path):
    try:
        drive_client.update_file(*args)
    except IndexError and Exception:
        drive_client = Drive(json_path)
        drive_client.update_file(*args)
    return drive_client


async def telegram_editor(text, print_text):
    try:
        message = await bot.edit_message_text(code(text), -1001376067490, server['lot_updater'], parse_mode='HTML')
        response = message['text'].split('/')
    except IndexError and Exception:
        print_text += ' (пост не изменился)'
        response = text.split('/')
    printer(print_text)
    return response


@dispatcher.edited_channel_post_handler()
async def detector(message: types.Message):
    try:
        if message['chat']['id'] == -1001376067490 and message['message_id'] == server['new_lot_id']:
            Mash.detector(message, old2, db_path=path['active'])
    except IndexError and Exception:
        await executive(str(message))


def lots_upload():
    drive_client = Drive(server['json4'])
    while True:
        try:
            sleep(20)
            if storage_start is False:
                printer('начало')
                drive_client = drive_updater(drive_client, server['lots'], server['json4'])
                printer('конец')
        except IndexError and Exception:
            thread_executive()


async def telegram():
    while True:
        try:
            db = SQLighter(path['active'])
            sleep(20)
            lots_raw = query('https://t.me/lot_updater/' + str(server['lot_updater']), '(.*)')
            if lots_raw:
                array = lots_raw.group(1).split('/')
                row = '/'
                for i in array:
                    if i != '':
                        row += i + '/'
                au_id = secure_sql(db.get_actives_id)
                for i in au_id:
                    if str(i) not in array:
                        if len(row) < 4085:
                            row += str(i) + '/'
                array = await telegram_editor(row, 'добавил новые лоты в telegram')
                for i in array:
                    if i != '':
                        if int(i) not in au_id:
                            row = re.sub('/' + str(i) + '/', '/', row)
                await telegram_editor(row, 'удалил закончившиеся из telegram')

        except IndexError and Exception:
            await executive()


def lot_updater():
    drive_client = Drive(server['json3'])
    local_limit = copy(global_limit)
    while True:
        try:
            printer('начало')
            stamp_updater = time_now()
            db_lots = SQLighter(path['lots'])
            db_active = SQLighter(path['active'])

            local_limit = Mash.multiple_requests(global_limit, local_limit)

            point = 0
            delete_lots_id = []
            sql_request_line = ''
            start_sql_request = Mash.create_start_sql_request()
            not_actives = secure_sql(db_active.get_not_actives)
            for lot in not_actives:
                point += 1
                if lot['stamp'] < time_now() - 3 * 60 * 60:
                    delete_lots_id.append(lot['au_id'])
                for lot_property in lot:
                    sql_request_line += "'" + str(lot.get(lot_property)) + "', "
                sql_request_line = sql_request_line[:-2] + '), ('
                if point == 1000:
                    secure_sql(db_lots.custom_sql, start_sql_request + sql_request_line[:-3] + ';')
                    sql_request_line = ''
                    point = 0
            if sql_request_line:
                secure_sql(db_lots.custom_sql, start_sql_request + sql_request_line[:-3] + ';')

            sql_request_line = ''
            start_sql_request = 'DELETE FROM lots WHERE au_id IN ('
            for au_id in delete_lots_id:
                sql_request_line += str(au_id) + ', '
            if sql_request_line:
                secure_sql(db_active.custom_sql, start_sql_request + sql_request_line[:-2] + ');')

            if time_now() - stamp_updater <= 4:
                sleep(4)
            drive_client = drive_updater(drive_client, server['active'], server['json3'])
            printer('конец')
        except IndexError and Exception:
            thread_executive()


def storage():
    global old2, global_limit, storage_start
    try:
        old = 0
        point = 0
        repository = []
        params_list = {}
        sql_request_line = ''
        db = SQLighter(path['lots'])
        start_sql_request = Mash.create_start_sql_request()
        for s in reversed(client1.list_spreadsheet_files()):
            if s['name'] in [i + server['storage'] for i in ['', 'temp-']]:
                for worksheet in client1.open(s['name']).worksheets():
                    for value in worksheet.col_values(1):
                        if len(value) > 1:
                            lot = Mash.form(value, depth='light')
                            if int(lot['au_id']) > old:
                                old = int(lot['au_id'])
                            if lot['base'] != 'None':
                                if lot['params'] != 'None':
                                    if lot['params'] not in params_list:
                                        params_list[lot['params']] = [lot['item_name']]
                                    else:
                                        if lot['item_name'] not in params_list[lot['params']]:
                                            params_list[lot['params']].append(lot['item_name'])
                                for lot_property in lot:
                                    if lot_property != 'raw':
                                        sql_request_line += "'" + str(lot.get(lot_property)) + "', "
                                sql_request_line = sql_request_line[:-2] + '), ('
                                point += 1
                                if point == 1000:
                                    secure_sql(db.custom_sql, start_sql_request + sql_request_line[:-3] + ';')
                                    sql_request_line = ''
                                    point = 0
                            else:
                                repository.append(lot)
                    if sql_request_line:
                        secure_sql(db.custom_sql, start_sql_request + sql_request_line[:-3] + ';')
                        sql_request_line = ''
                        point = 0
        for lot in repository:
            params_item_names = params_list.get(lot['params'])
            if params_item_names:
                for item_name in params_item_names:
                    if item_name in lot['item_name']:
                        lot = Mash.engrave(item_name, lot)
                        break
            if lot['base'] == 'None':
                temp = []
                for item_name in const_base:
                    if item_name in lot['item_name'] \
                            and const_base[item_name][0] in allowed_params_engrave:
                        temp.append(item_name)
                if len(temp) >= 1:
                    item_name = temp[0]
                    for temp_name in temp:
                        if temp_name > item_name:
                            item_name = temp_name
                    lot = Mash.engrave(item_name, lot)
            for lot_property in lot:
                if lot_property != 'raw':
                    sql_request_line += "'" + str(lot.get(lot_property)) + "', "
            sql_request_line = sql_request_line[:-2] + '), ('
            point += 1
            if point == 1000:
                secure_sql(db.custom_sql, start_sql_request + sql_request_line[:-3] + ';')
                sql_request_line = ''
                point = 0
        if sql_request_line:
            secure_sql(db.custom_sql, start_sql_request + sql_request_line[:-3] + ';')

        old += 1
        if old2 == 0:
            old2 = old

        dev_message = edit_dev_message(s_message, '\n' + log_time(tag=code))
        request_array = []
        global_limit = 150
        db_active = SQLighter(path['active'])
        currently_active = secure_sql(db_active.get_all_au_id)
        for au_id in range(old, old2):
            if au_id not in currently_active:
                request_array.append(au_id)
        printer('мы уже тут ебать')
        Mash.multiple_requests(global_limit, local_limit=150, request_array=request_array, storage=True)
        edit_dev_message(dev_message, '\n' + log_time(tag=code))
        printer('закончил работу')
        storage_start = False
        sleep(60)
        global_limit = 300
        _thread.exit()
    except IndexError and Exception:
        thread_executive()


def messages():
    global const_base
    drive_client = Drive(server['json2'])
    while True:
        if storage_start is False:
            try:
                sleep(10)
                const = {}
                stats = {}
                printer('начало')
                qualities = ['None']
                db = SQLighter(path['lots'])
                client2 = gspread.service_account(server['json2'])
                qualities = append_values(qualities, secure_sql(db.get_dist_quality))
                const_items = client2.open('Notify').worksheet('items').get('A1:B50000', major_dimension='ROWS')
                temp_base = {re.sub('️', '', item[0]): item[1] for item in const_items}
                const_reversed_base = {value: key for key, value in temp_base.items()}
                time_week = time_now() - (7 * 24 * 60 * 60)
                const_base = copy(temp_base)
                for base in const_reversed_base:
                    const[base] = {}
                    stats[base] = {}
                    for quality in qualities:
                        stats[base][quality] = {'costs_list_full': [], 'costs_list_week': [],
                                                'unsold_count_full': 0, 'unsold_count_week': 0,
                                                'cancelled_count_full': 0, 'cancelled_count_week': 0}

                lots = secure_sql(db.get_not_actives)
                for lot in lots:
                    if lot['base'] != 'None' and lot['quality']:
                        qualities = ['None']
                        if lot['quality'] != 'None':
                            qualities.insert(0, lot['quality'])
                        else:
                            qualities.insert(0, 'Common')

                        for quality in qualities:
                            if lot['status'] != 'Cancelled':
                                if lot['b_castle'] != 'None':
                                    stats[lot['base']][quality]['costs_list_full'].append(lot['cost'])
                                    if lot['stamp'] >= time_week:
                                        stats[lot['base']][quality]['costs_list_week'].append(lot['cost'])
                                else:
                                    stats[lot['base']][quality]['unsold_count_full'] += 1
                                    if lot['stamp'] >= time_week:
                                        stats[lot['base']][quality]['unsold_count_week'] += 1
                            else:
                                stats[lot['base']][quality]['cancelled_count_full'] += 1
                                if lot['stamp'] >= time_week:
                                    stats[lot['base']][quality]['cancelled_count_week'] += 1
                for base in stats:
                    for quality in list(stats[base]):
                        if quality != 'None' and stats[base][quality] == clear_stats:
                            del stats[base][quality]

                for base in stats:
                    if len(stats[base]) == 2:
                        qualities = []
                        for quality in stats[base]:
                            qualities.append(quality)
                        if stats[base][qualities[0]] == stats[base][qualities[1]]:
                            del stats[base][qualities[1]]

                for base in stats:
                    for quality in stats[base]:
                        const[base][quality] = {'cost': '0/0', 'stats': ''}
                        costs_list_full = stats[base][quality]['costs_list_full']
                        text = '__' + bold('{0} ') + str(len(costs_list_full)) + '__'
                        for title in ['{1}', '{2}']:
                            text += bold(title) + '_'
                            median = 0
                            minimum = 0
                            maximum = 0
                            average = 0
                            last_sold = ''
                            if title == '{1}':
                                costs_list = costs_list_full
                                unsold_count = stats[base][quality]['unsold_count_full']
                                cancelled_count = stats[base][quality]['cancelled_count_full']
                            else:
                                costs_list = stats[base][quality]['costs_list_week']
                                unsold_count = stats[base][quality]['unsold_count_week']
                                cancelled_count = stats[base][quality]['cancelled_count_week']
                            if len(costs_list) > 0:
                                minimum = min(costs_list)
                                maximum = max(costs_list)
                                cost = const[base][quality]['cost']
                                median = median_function(costs_list)
                                average = round(mean(costs_list), 2)
                                median = int(median) if float(median).is_integer() else median
                                if title == '{2}':
                                    pattern, median_text = '/\d+', '/' + str(median)
                                    last_sold = '_{8} ' + str(costs_list[-1])
                                else:
                                    pattern, median_text = '\d+/', str(median) + '/'
                                const[base][quality]['cost'] = re.sub(pattern, median_text, cost)
                            text += '{3} ' + str(median) + '_' + \
                                '{4} ' + str(average) + '_' + \
                                '{5} ' + str(minimum) + '/' + str(maximum) + '_' + \
                                '{6} ' + str(cancelled_count) + '_' + \
                                '{7} ' + str(unsold_count) + '/' + str(len(costs_list) + unsold_count) + \
                                last_sold + '__'
                        const[base][quality]['stats'] = text
                with codecs.open('storage.json', 'w', 'utf-8') as doc:
                    for base in const_reversed_base:
                        const[const_reversed_base[base]] = const.pop(base)
                    doc.write(str(const))
                    doc.close()
                drive_client = drive_updater(drive_client, server['storage_file'], server['json2'])
                printer('конец')
            except IndexError and Exception:
                thread_executive()


@dispatcher.message_handler()
async def repeat_all_messages(message: types.Message):
    try:
        if message['chat']['id'] != idMe:
            await bot.send_message(message['chat']['id'], 'К тебе этот бот не имеет отношения, уйди пожалуйста')
        else:
            if message['text'].lower().startswith('/log'):
                modified = re.sub('/log_', '', message['text'].lower())
                if modified.startswith('s'):
                    doc = open(path['storage'], 'rb')
                elif modified.startswith('a'):
                    doc = open(path['active'], 'rb')
                else:
                    doc = open('log.txt', 'rt')
                await bot.send_document(idMe, doc)
            elif message['text'].lower().startswith('/lots'):
                size = round(os.path.getsize(path['lots']) / (1024 * 1024), 2)
                text_size = 'Размер (' + code(path['lots']) + '): ' + bold(size) + ' MB'
                await bot.send_message(message['chat']['id'], text_size)
            else:
                await bot.send_message(message['chat']['id'], 'Я работаю', reply_markup=None)
    except IndexError and Exception:
        await executive(str(message))


if __name__ == '__main__':
    threads = [storage, lot_updater, lots_upload, messages]
    for thread_element in threads:
        _thread.start_new_thread(thread_element, ())
    dispatcher.loop.create_task(telegram())
    executor.start_polling(dispatcher)
