# -*- coding: utf-8 -*-
import os
import re
import codecs
import asyncio
import gspread
import _thread
from time import sleep
import concurrent.futures
from SQL import SQLighter
from statistics import mean
import functions as objects
from ast import literal_eval
from datetime import datetime
from copy import copy, deepcopy
from additional.GDrive import Drive
from statistics import median as median_function
from telethon.sync import TelegramClient, events
from additional.game_objects import Mash, path, symbols, allowed_lists
from functions import code, bold, printer, log_time, time_now, secure_sql, sql_divide, append_values
# =====================================================================================================================
if __name__ == '__main__':
    import environ
    print('Запуск с окружением', environ.environ)


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
        if file['name'] in [f"{os.environ['session1']}.session", f"{os.environ['session2']}.session"]:
            client.download_file(file['id'], file['name'])
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
# =====================================================================================================================


def error_handler():
    try:
        ErrorAuth.executive(None)
    except IndexError and Exception:
        pass


def drive_updater(drive_client, args, json_path):
    try:
        drive_client.update_file(*args)
    except IndexError and Exception:
        drive_client = Drive(json_path)
        drive_client.update_file(*args)
    return drive_client


async def update_lots(client: TelegramClient, ids: list) -> None:
    messages = await client.get_messages(server['channel'], ids=ids)
    for message in messages:
        if message and message.id and message.message:
            Mash.update_db_lot(f"{message.id}/{re.sub('/', '&#47;', message.message)}".replace('\n', '/'))


def lot_database_updater():
    global updates
    while True:
        try:
            Mash.update_db_lot(updates.pop(0)) if updates else None
            sleep(0.05)
        except IndexError and Exception:
            error_handler()


def lot_detector():
    global updates
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        client = TelegramClient(
            os.environ['session1'], int(os.environ['api_id']), os.environ['api_hash'])
        with client:
            @client.on(events.NewMessage(chats=server['channel']))
            @client.on(events.MessageEdited(chats=server['channel']))
            async def handler(response):
                if response.message and response.message.id and response.message.message:
                    upd = f"{response.message.id}/{re.sub('/', '&#47;', response.message.message)}".replace('\n', '/')
                    updates.append(upd), printer(f'Обновление: {upd}')
            printer(f"detector() в работе: {server['channel']}")
            client.run_until_disconnected()
    except IndexError and Exception:
        error_handler()
        _thread.start_new_thread(lot_detector, ())


def lot_telegram_updater():
    global lot_telegram_updater_closed
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        client = TelegramClient(
            os.environ['session2'], int(os.environ['api_id']), os.environ['api_hash'])
    except IndexError and Exception:
        error_handler()
        printer('Вылет lot_telegram_updater(), ждем 20 сек и перезапускаем')
        sleep(20)
        _thread.start_new_thread(lot_telegram_updater, ())
        _thread.exit()
    printer('Запуск lot_telegram_updater()')
    while True:
        try:
            actives = secure_sql(SQLighter(path['active']).get_actives_id)
            with client:
                client.loop.run_until_complete(update_lots(client, actives))
            if storage_lock is True:
                printer('Завершаем lot_telegram_updater() до окончания обновления лотов в storage()')
                lot_telegram_updater_closed = True
                _thread.exit()
            sleep(8)
        except IndexError and Exception:
            error_handler()


def lot_uploader():
    counter, drive_lots, drive_active = 0, Drive(server['json4']), Drive(server['json3'])
    while True:
        try:
            counter += 1
            stamp = datetime.now().timestamp()
            now, db_active, delete_lots_id = time_now(), SQLighter(path['active']), []
            for lot in secure_sql(db_active.get_ended_lots):
                if lot['status'] != '#active' and lot['stamp'] < now - 600:
                    delete_lots_id.append(str(lot['au_id']))

            if delete_lots_id:
                secure_sql(db_active.custom_sql, f"DELETE FROM lots WHERE au_id IN ({', '.join(delete_lots_id)});")

            if os.environ.get('server') != 'local':
                drive_active = drive_updater(drive_active, server['active_file'], server['json3'])
                if storage_start is False and counter >= 5:
                    printer(f"{path['active']} синхронизирован, {counter} раз")
                    counter, drive_lots = 0, drive_updater(drive_lots, server['lots_file'], server['json4'])
                    printer(f"{path['lots']} синхронизирован")

            delay = 4 - (datetime.now().timestamp() - stamp)
            sleep(0 if delay < 0 else delay)
        except IndexError and Exception:
            error_handler()


def stats_calculator():
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
                error_handler()


def storage(s_message):
    global server, storage_lock, storage_start
    try:
        old = 0
        repository = []
        sql_request = ''
        params_list = {}
        printer('начало')
        db = SQLighter(path['lots'])
        client = gspread.service_account(server['json2'])
        start_sql_request = Mash.create_start_sql_request()
        for s in reversed(client.list_spreadsheet_files()):
            if s['name'] in [pre + server['storage'] for pre in ['', 'temp-']]:
                sheet, titles = client.open(s['name']), []
                print('HELLO', server['json2'], s['name'])
                for i in range(0, 1 if os.environ.get('server') == 'local' else 45):
                    checker = sheet.get_worksheet(i)
                    titles.append(checker.title) if checker else None
                print(titles)
                for title in titles:
                    stamp = datetime.now().timestamp()
                    worksheet = sheet.worksheet(title)
                    for lots in sql_divide(worksheet.col_values(1)):
                        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as future_executor:
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
                    if s_message:
                        s_message = deepcopy(Auth.edit_dev_message(
                            s_message, f"\nworksheet-{worksheet.title} {datetime.now().timestamp() - stamp}"))
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
            s_message = deepcopy(Auth.edit_dev_message(s_message, f"\n{log_time(tag=code)}"))

        storage_lock = True

        try:
            print('Ждем завершения lot_telegram_updater')
            while lot_telegram_updater_closed is False:
                sleep(1)
            not_stored = range(old, server['lot_barrier'] + 1)
            print('DIFF', not_stored)
            asyncio.set_event_loop(asyncio.new_event_loop())
            telegram_client = TelegramClient(
                os.environ['session2'], int(os.environ['api_id']), os.environ['api_hash'])
            with telegram_client:
                telegram_client.loop.run_until_complete(update_lots(telegram_client, list(not_stored)))
        except IndexError and Exception:
            error_handler()

        storage_lock = False
        _thread.start_new_thread(lot_telegram_updater, ())

        if s_message:
            Auth.edit_dev_message(s_message, f"\n{log_time(tag=code)}")
        printer('закончил работу')
        storage_start = False
        _thread.exit()
    except IndexError and Exception:
        error_handler()


server = {}
updates = []
const_base = {}
storage_start = True

storage_lock = False
lot_telegram_updater_closed = False

clear_stats = {'costs_list_full': [], 'costs_list_week': [],
               'unsold_count_full': 0, 'unsold_count_week': 0,
               'cancelled_count_full': 0, 'cancelled_count_week': 0}
functions = [starting_const_creation, starting_server_creation, starting_active_db_creation, starting_new_lot]
ErrorAuth = objects.AuthCentre(os.environ['ERROR-TOKEN'])
Auth = objects.AuthCentre(os.environ['DEV-TOKEN'])
spreadsheet = create_server_json_list()
objects.concurrent_functions(functions)
# ========================================================================================================
Mash = Mash(server, const_base)


def start(stamp):
    if os.environ.get('server') == 'local':
        threads, start_message = [lot_uploader, lot_database_updater, lot_telegram_updater], None
        start_message = Auth.start_message(stamp)
    else:
        start_message = Auth.start_message(stamp)
        threads = [lot_detector, lot_uploader, stats_calculator, lot_database_updater, lot_telegram_updater]
    _thread.start_new_thread(storage, (start_message,))
    for thread_element in threads:
        _thread.start_new_thread(thread_element, ())
    while True:
        sleep(5000)


if os.environ.get('server') == 'local':
    start(time_now())
