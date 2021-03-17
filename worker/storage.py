# -*- coding: utf-8 -*-
import os
import re
import codecs
import gspread
import objects
import _thread
from time import sleep
import concurrent.futures
from aiogram import types
from SQL import SQLighter
from statistics import mean
from ast import literal_eval
from copy import copy, deepcopy
from aiogram.utils import executor
from additional.GDrive import Drive
from aiogram.dispatcher import Dispatcher
from statistics import median as median_function
from additional.game_objects import Mash, path, symbols, allowed_lists
from objects import code, bold, printer, log_time, time_now, secure_sql, sql_divide, append_values
# ========================================================================================================


def create_server_json_list():
    global server
    server['non_emoji_symbols'] = symbols
    created_files = objects.environmental_files(python=True)
    for file_name in created_files:
        search_json = re.search(r'(\d)\.json', file_name)
        if search_json:
            server[f'json{search_json.group(1)}'] = file_name
    return gspread.service_account(server['json2']).open('Notify')


def starting_new_lot():
    global server
    while server.get('link: new_lot_id') is None:
        pass
    search = objects.query(server['link: new_lot_id'], r'(\d+?)/')
    if search:
        server['lot_barrier'] = int(search.group(1)) + 1
    else:
        server['lot_barrier'] = 0
    return f"Переменная server['lot_barrier'] = {server['lot_barrier']} загружена"


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


def starting_active_db_creation():
    global server
    client = Drive(server['json2'])
    files = client.files()
    folder = 'None'
    while server.get('storage') is None:
        pass
    for file in files:
        if file['name'] == f"{server['storage']}_folder":
            folder = file['id']
            break
    for file in files:
        if file.get('parents') and folder == file['parents'][0]:
            for key in path:
                if key in file['name']:
                    server[f'{key}_file'] = [file['id'], path[key]]
                    if key == 'active':
                        client.download_file(*server[f'{key}_file'])
    return f"{path['active']} загружен"


def starting_server_creation():
    resources = spreadsheet.worksheet('resources').get('A1:Z50000', major_dimension='COLUMNS')
    options = resources.pop(0)
    for option in options:
        for resource in resources:
            if resource[0] == os.environ['server'] and option != 'options':
                value = resource[options.index(option)]
                if option in ['castle_list', 'storage', 'channel']:
                    server[option] = value
                if option == 'DATA_TOKEN':
                    server['TOKEN'] = value
                elif option == 'form':
                    server[option] = literal_eval(re.sub('️', '', value))
                elif option == 'channel':
                    server[f'link: {option}'] = f'https://t.me/s/{value}/'
                elif option == 'new_lot_id':
                    server[f'link: {option}'] = f'https://t.me/lot_updater/{value}'
                    server[option] = int(value)
    return 'Серверная константа загружена'
# ========================================================================================================


def drive_updater(drive_client, args, json_path):
    try:
        drive_client.update_file(*args)
    except IndexError and Exception:
        drive_client = Drive(json_path)
        drive_client.update_file(*args)
    return drive_client


def lots_upload():
    drive_client = Drive(server['json4'])
    while True:
        try:
            sleep(20)
            if storage_start is False:
                drive_client = drive_updater(drive_client, server['lots_file'], server['json4'])
                printer(f"{path['lots']} синхронизирован")
        except IndexError and Exception:
            ErrorAuth.thread_exec()


def lot_updater():
    drive_client = Drive(server['json3'])
    while True:
        try:
            db_lots = SQLighter(path['lots'])
            db_active = SQLighter(path['active'])
            actives = secure_sql(db_active.get_actives_id)
            delay, responses = Mash.multiple_requests(actives, global_limit, max_workers)
            delay -= Mash.multiple_db_updates(responses, max_workers)

            sql_request = ''
            delete_lots_id = []
            start_sql_request = Mash.create_start_sql_request()

            for lots in sql_divide(secure_sql(db_active.get_ended_lots)):
                for lot in lots:
                    if lot['stamp'] < time_now() - 3 * 60 * 60:
                        delete_lots_id.append(lot['au_id'])
                    for key in lot:
                        sql_request += f"'{lot.get(key)}', "
                    sql_request = f'{sql_request[:-2]}), ('
                if sql_request:
                    secure_sql(db_lots.custom_sql, f'{start_sql_request}{sql_request[:-3]};')
                    sql_request = ''

            sql_request = ''
            start_sql_request = 'DELETE FROM lots WHERE au_id IN ('
            for au_id in delete_lots_id:
                sql_request += f'{au_id}, '
            if sql_request:
                secure_sql(db_active.custom_sql, f'{start_sql_request}{sql_request[:-2]});')

            if os.environ.get('server') != 'local':
                drive_client = drive_updater(drive_client, server['active_file'], server['json3'])
            delay = 4 if delay <= 4 else delay
            sleep(delay)
        except IndexError and Exception:
            ErrorAuth.thread_exec()


def storage(s_message):
    from datetime import datetime
    global server, max_workers, global_limit, storage_start
    try:
        old = 0
        repository = []
        sql_request = ''
        params_list = {}
        printer('начало')
        dev_message = None
        db = SQLighter(path['lots'])
        client = gspread.service_account(server['json2'])
        start_sql_request = Mash.create_start_sql_request()
        for s in reversed(client.list_spreadsheet_files()):
            if s['name'] in [pre + server['storage'] for pre in ['', 'temp-']]:
                for worksheet in client.open(s['name']).worksheets():
                    stamp = datetime.now().timestamp()
                    for lots in sql_divide(worksheet.col_values(1)):
                        with concurrent.futures.ThreadPoolExecutor(max_workers=9) as future_executor:
                            futures = []
                            for future in lots:
                                futures.append(future_executor.submit(Mash.form, future, depth='light'))
                            for future in concurrent.futures.as_completed(futures):
                                lot = future.result()
                                if lot:
                                    old = lot['au_id'] if lot['au_id'] > old else old
                                    if lot['base'] != 'None':
                                        sql_lot = ''
                                        if lot['params'] != 'None':
                                            if lot['params'] not in params_list:
                                                params_list[lot['params']] = [lot['item_name']]
                                            else:
                                                if lot['item_name'] not in params_list[lot['params']]:
                                                    params_list[lot['params']].append(lot['item_name'])
                                        for key in lot:
                                            sql_lot += f"'{lot.get(key)}', "
                                        sql_request += f'{sql_lot[:-2]}), ('
                                    else:
                                        repository.append(lot)
                        if sql_request:
                            secure_sql(db.custom_sql, f'{start_sql_request}{sql_request[:-3]};')
                            sql_request = ''
                    print(f'worksheet-{worksheet.title}', datetime.now().timestamp() - stamp)
        for lots in sql_divide(repository):
            for lot in lots:
                params_item_names = params_list.get(lot['params'])
                if params_item_names:
                    for item_name in params_item_names:
                        if item_name in lot['item_name']:
                            lot = Mash.engrave(item_name, lot)
                            break
                if lot['base'] == 'None':
                    names = []
                    for item_name in const_base:
                        if item_name in lot['item_name'] \
                                and const_base[item_name][0] in allowed_lists['engrave']:
                            names.append(item_name)
                    if len(names) >= 1:
                        item_name = names[0]
                        for name in names:
                            if len(name) > len(item_name):
                                item_name = name
                        lot = Mash.engrave(item_name, lot)
                for key in lot:
                    sql_request += f"'{lot.get(key)}', "
                sql_request = f'{sql_request[:-2]}), ('
            if sql_request:
                secure_sql(db.custom_sql, f'{start_sql_request}{sql_request[:-3]};')
                sql_request = ''

        old += 1
        if server['lot_barrier'] == 0:
            server['lot_barrier'] = old
        if s_message:
            dev_message = deepcopy(Auth.edit_dev_message(s_message, f"\n{log_time(tag=code)}"))

        request_array = []
        currently_active = secure_sql(SQLighter(path['active']).get_all_au_id)
        for au_id in range(old, server['lot_barrier']):
            if au_id not in currently_active:
                request_array.append(au_id)
        delay, responses = Mash.multiple_requests(request_array, full_limit=200)
        Mash.multiple_db_updates(responses, lot_updater=False)
        if dev_message:
            Auth.edit_dev_message(dev_message, f"\n{log_time(tag=code)}")
        printer('закончил работу')
        storage_start = False
        sleep(60)
        global_limit = 300
        max_workers = 10
        _thread.exit()
    except IndexError and Exception:
        ErrorAuth.thread_exec()


def messages():
    global const_base
    drive_client = Drive(server['json2'])
    while True:
        if storage_start is False:
            try:
                const = {}
                printer('начало')
                qualities = ['None']
                db = SQLighter(path['lots'])
                client = gspread.service_account(server['json2'])
                qualities = append_values(qualities, secure_sql(db.get_dist_quality))
                const_items = client.open('Notify').worksheet('items').get('A1:B50000', major_dimension='ROWS')
                temp_base = {re.sub('️', '', item[0]): item[1] for item in const_items}
                const_reversed_base = {value: key for key, value in temp_base.items()}
                time_week = time_now() - (7 * 24 * 60 * 60)
                const_base = copy(temp_base)
                for base in const_reversed_base:
                    stats = {}
                    const[base] = {}
                    lots = secure_sql(db.get_not_actives_by_base, base)
                    for quality in qualities:
                        stats[quality] = {'costs_list_full': [], 'costs_list_week': [],
                                          'unsold_count_full': 0, 'unsold_count_week': 0,
                                          'cancelled_count_full': 0, 'cancelled_count_week': 0}
                    for lot in lots:
                        if lot['base'] == base and lot['quality']:
                            for quality in qualities:
                                if lot['quality'] == quality or quality == 'None' or \
                                        (quality == 'Common' and lot['quality'] == 'None'):
                                    if lot['status'] != 'Cancelled':
                                        if lot['b_castle'] != 'None':
                                            stats[quality]['costs_list_full'].append(lot['cost'])
                                            if lot['stamp'] >= time_week:
                                                stats[quality]['costs_list_week'].append(lot['cost'])
                                        else:
                                            stats[quality]['unsold_count_full'] += 1
                                            if lot['stamp'] >= time_week:
                                                stats[quality]['unsold_count_week'] += 1
                                    else:
                                        stats[quality]['cancelled_count_full'] += 1
                                        if lot['stamp'] >= time_week:
                                            stats[quality]['cancelled_count_week'] += 1

                    for quality in list(stats):
                        if quality != 'None' and stats[quality] == clear_stats:
                            del stats[quality]

                    if len(stats) == 2:
                        if stats.get('None') and stats.get('Common'):
                            if stats['None'] == stats['Common']:
                                del stats['Common']

                    for quality in qualities:
                        if stats.get(quality):
                            const[base][quality] = {'cost': '0/0', 'stats': ''}
                            costs_list_full = stats[quality]['costs_list_full']
                            text = bold('{0} ') + str(len(costs_list_full)) + '__'
                            for title in ['{1}', '{2}']:
                                median = 0
                                minimum = 0
                                maximum = 0
                                average = 0
                                last_sold = ''
                                text += bold(title) + '_'
                                if title == '{1}':
                                    last_sold = '__'
                                    costs_list = costs_list_full
                                    unsold_count = stats[quality]['unsold_count_full']
                                    cancelled_count = stats[quality]['cancelled_count_full']
                                else:
                                    costs_list = stats[quality]['costs_list_week']
                                    unsold_count = stats[quality]['unsold_count_week']
                                    cancelled_count = stats[quality]['cancelled_count_week']
                                if len(costs_list) > 0:
                                    minimum = min(costs_list)
                                    maximum = max(costs_list)
                                    cost = const[base][quality]['cost']
                                    median = median_function(costs_list)
                                    average = round(mean(costs_list), 2)
                                    median = int(median) if float(median).is_integer() else median
                                    if title == '{2}':
                                        last_sold = '_{8} ' + str(costs_list[-1])
                                        pattern, median_text = r'/\d+', '/' + str(median)
                                    else:
                                        pattern, median_text = r'\d+/', str(median) + '/'
                                    const[base][quality]['cost'] = re.sub(pattern, median_text, cost)
                                text += '{3} ' + str(median) + '_' + \
                                    '{4} ' + str(average) + '_' + \
                                    '{5} ' + str(minimum) + '/' + str(maximum) + '_' + \
                                    '{6} ' + str(cancelled_count) + '_' + \
                                    '{7} ' + str(unsold_count) + '/' + str(len(costs_list) + unsold_count) + \
                                    last_sold
                            const[base][quality]['stats'] = text

                with codecs.open('storage.json', 'w', 'utf-8') as doc:
                    for base in const_reversed_base:
                        const[const_reversed_base[base]] = const.pop(base)
                    doc.write(str(const))
                    doc.close()
                drive_client = drive_updater(drive_client, server['storage_file'], server['json2'])
                printer('конец')
            except IndexError and Exception:
                ErrorAuth.thread_exec()


server = {}
const_base = {}
max_workers = 5
global_limit = 100
storage_start = True
clear_stats = {'costs_list_full': [], 'costs_list_week': [],
               'unsold_count_full': 0, 'unsold_count_week': 0,
               'cancelled_count_full': 0, 'cancelled_count_week': 0}
functions = [starting_const_creation, starting_server_creation, starting_active_db_creation, starting_new_lot]
ErrorAuth = objects.AuthCentre(os.environ['ERROR-TOKEN'])
Auth = objects.AuthCentre(os.environ['DEV-TOKEN'])
spreadsheet = create_server_json_list()
objects.concurrent_functions(functions)
# ========================================================================================================
bot = objects.AuthCentre(server['TOKEN']).start_main_bot('async')
Mash = Mash(server, const_base)
dispatcher = Dispatcher(bot)


@dispatcher.edited_channel_post_handler()
async def detector(message: types.Message):
    try:
        if message['chat']['id'] == -1001376067490 and message['message_id'] == server['new_lot_id']:
            Mash.detector(message, server['lot_barrier'], Auth, db_path=path['active'])
    except IndexError and Exception:
        await ErrorAuth.async_exec(str(message))


def start(stamp):
    start_message = None
    threads = [lot_updater]
    if os.environ.get('server') != 'local':
        start_message = Auth.start_message(stamp)
        threads = [lot_updater, lots_upload, messages]
    _thread.start_new_thread(storage, (start_message,))
    for thread_element in threads:
        _thread.start_new_thread(thread_element, ())
    executor.start_polling(dispatcher)

    ErrorAuth.start_message(stamp, f"\nОшибка с переменными окружения.\n{bold('Бот выключен')}")


if os.environ.get('server') == 'local':
    start(time_now())
