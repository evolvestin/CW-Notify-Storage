# -*- coding: utf-8 -*-
import os
import re
import asyncio
import gspread
import _thread
import requests
from time import sleep
import concurrent.futures
from copy import deepcopy
from aiogram import types
from statistics import mean
from ast import literal_eval
from bs4 import BeautifulSoup
from datetime import datetime
from settings import base_dir
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from statistics import median as median_function
from telethon.sync import TelegramClient, events

from functions.SQL import SQL
from functions.GDrive import Drive
from functions.lot_handler import LotHandler, raw_symbols
from functions.objects import code, bold, time_now, AuthCentre, environmental_files
# =====================================================================================================================


def starting_session_creation():
    client = Drive(server['json2'])
    for file in client.files():
        if file['name'] in [f"{os.environ['session1']}.session", f"{os.environ['session2']}.session"]:
            client.download_file(file['id'], file['name'])


def create_server_json_list():
    _server, created_files = {}, environmental_files(base_dir.joinpath('.'), python=True)
    for file_name in created_files:
        search_json = re.search(r'(\d)\.json', file_name)
        _server.update({f'json{search_json.group(1)}': file_name}) if search_json else None
    _server.update({'start_message': None, 'storage_reload': False,
                    'spreadsheet': gspread.service_account(_server['json2']).open('Notify')})
    return _server


def starting_items_creation(spreadsheet=None):
    global server
    emojis, item_names = '', {}
    spreadsheet = spreadsheet if spreadsheet is not None else server['spreadsheet']
    rows = spreadsheet.worksheet('items2').get('A1:Z50000', major_dimension='ROWS')
    allowed_to = {header.lower().strip(): [] for header in rows.pop(0)[2:]}
    for row in rows:
        if len(row) >= 2:
            item_name = re.sub('️', '', row[0]).replace('\'', '&#39;')
            item_names.update({item_name: row[1].strip()})
            emoji = re.sub(raw_symbols, '', item_name)
            emojis += emoji if emoji not in emojis and len(emoji) > 0 else ''
            allowed_to['params'].append(item_name) if len(row) >= 3 and row[2].strip() else None
            allowed_to['engrave'].append(item_name) if len(row) >= 4 and row[3].strip() else None
    server.update({'allowed_to': allowed_to, 'item_names': item_names, 'symbols': raw_symbols.format(emojis, '{}')})


def starting_server_creation():
    resources = server['spreadsheet'].worksheet('resources').get('A1:Z50000', major_dimension='COLUMNS')
    options = resources.pop(0)
    for option in options:
        for resource in resources:
            if resource[0] == os.environ['server'] and option != 'options':
                value = resource[options.index(option)]
                if option in ['castle_list', 'storage', 'channel']:
                    server.update({option: value})
                elif option == 'DATA_TOKEN':
                    server.update({'TOKEN': value})
                elif option == 'form':
                    server.update({option: literal_eval(re.sub('️', '', value))})
                elif option == 'channel':
                    server.update({f'link: {option}': f'https://t.me/s/{value}/'})
                elif option == 'new_lot_id':
                    server.update({option: int(value), f'link: {option}': f'https://t.me/lot_updater/{value}'})
# =====================================================================================================================


server = create_server_json_list()
starting_functions = [starting_items_creation, starting_server_creation, starting_session_creation]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as future_executor:
    starting_functions = [future_executor.submit(future) for future in starting_functions]
    [future.result() for future in concurrent.futures.as_completed(starting_functions)]
lot_handler = LotHandler(server)
Auth = AuthCentre(GMT=3, ID_DEV=int(os.environ['ID_DEV']), TOKEN=server['TOKEN'])
bot, dispatcher = Auth.async_bot, Dispatcher(Auth.async_bot)
# =====================================================================================================================


async def update_lots(client: TelegramClient, ids: list) -> None:
    db = SQL()
    messages = await client.get_messages(server['channel'], ids=ids)
    for message in messages:
        lot = lot_handler.lot_from_message(message)
        db.update('lots', lot['post_id'], lot, commit=True) if lot.get('post_id') else None
    db.close()


@dispatcher.message_handler()
async def message_handler(message: types.Message):
    try:
        if message.chat.id > 0:
            if message.text == '/reload':
                text = 'Перезагружаем базу данных.'
                _thread.start_new_thread(storage_reloader, ())
            else:
                text = 'Бот статистики функционирует в штатном режиме.'
            await bot.send_message(message.chat.id, text, parse_mode='HTML')
    except IndexError and Exception:
        Auth.dev.async_except(message)


def start(stamp):
    global server
    if os.environ.get('server') == 'local':
        threads = [stats_calculator]
        server.update({'start_message': Auth.dev.start(stamp)})
    else:
        server.update({'start_message': Auth.dev.start(stamp)})
        threads = [lot_detector, stats_calculator, lot_telegram_updater]
    for thread_element in threads:
        _thread.start_new_thread(thread_element, ())
    executor.start_polling(dispatcher)


def lot_detector():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        client = TelegramClient(os.environ['session1'], int(os.environ['api_id']), os.environ['api_hash'])
        with client:
            @client.on(events.NewMessage(chats=server['channel']))
            @client.on(events.MessageEdited(chats=server['channel']))
            async def post_handler(response):
                if response:
                    lot = lot_handler.lot_from_message(response.message)
                    if lot.get('post_id'):
                        db = SQL()
                        db.update('lots', lot['post_id'], lot, commit=True)
                        db.close()
                    Auth.dev.printer(f'Обновление: {lot}')
            Auth.dev.printer(f"detector() в работе: {server['channel']}")
            client.run_until_disconnected()
    except IndexError and Exception:
        Auth.dev.executive(None)
        _thread.start_new_thread(lot_detector, ())


def lot_telegram_updater():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        client = TelegramClient(os.environ['session2'], int(os.environ['api_id']), os.environ['api_hash'])
    except IndexError and Exception:
        Auth.dev.executive(None)
        _thread.start_new_thread(lot_telegram_updater, ())
        _thread.exit()
    Auth.dev.printer('Запуск lot_telegram_updater()')
    while True:
        try:
            db = SQL()
            ids = [lot['post_id'] for lot in db.get_active_lots()]
            db.close()
            with client:
                client.loop.run_until_complete(update_lots(client, ids=ids))
            sleep(8)
        except IndexError and Exception as error:
            if re.search('relation "lots" does not exist', str(error)):
                sleep(15)
            else:
                Auth.dev.executive(None)
                _thread.start_new_thread(lot_telegram_updater, ())
                _thread.exit()


def stats_calculator():
    clear_stats = {'costs_list_full': [], 'costs_list_week': [],
                   'unsold_count_full': 0, 'unsold_count_week': 0,
                   'cancelled_count_full': 0, 'cancelled_count_week': 0}
    while True:
        if server['storage_reload'] is False:
            try:
                Auth.dev.printer('Начало')
                db = SQL()
                const, qualities = {}, [None]
                time_week = time_now() - (7 * 24 * 60 * 60)
                qualities.extend(db.get_distinct_qualities())
                item_ids = {value: key for key, value in server['item_names'].items()}
                starting_items_creation(gspread.service_account(server['json2']).open('Notify'))
                for item_id in item_ids:
                    stats = {}
                    stamp = datetime.now().timestamp()
                    const.update({item_id: {}})
                    for quality in qualities:
                        stats.update({quality: deepcopy(clear_stats)})
                    for lot in db.get_ended_lots_by_item_id(item_id):
                        for quality in qualities:
                            if (lot['quality'] == quality or quality is None
                                    or (quality == 'Common' and lot['quality'] is None)):
                                if lot['status'] != 'Cancelled':
                                    if lot['buyer_castle'] is not None:
                                        stats[quality]['costs_list_full'].append(lot['price'])
                                        if lot['stamp'] >= time_week:
                                            stats[quality]['costs_list_week'].append(lot['price'])
                                    else:
                                        stats[quality]['unsold_count_full'] += 1
                                        if lot['stamp'] >= time_week:
                                            stats[quality]['unsold_count_week'] += 1
                                else:
                                    stats[quality]['cancelled_count_full'] += 1
                                    if lot['stamp'] >= time_week:
                                        stats[quality]['cancelled_count_week'] += 1

                    for quality in list(stats):
                        if quality is not None and stats[quality] == clear_stats:
                            del stats[quality]

                    if len(stats) == 2 and stats.get(None) and stats.get('Common') and stats[None] == stats['Common']:
                        del stats['Common']

                    for quality in qualities:
                        if stats.get(quality):
                            const[item_id][quality] = {'cost': '0/0', 'stats': ''}
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
                                    cost = const[item_id][quality]['cost']
                                    median = median_function(costs_list)
                                    average = round(mean(costs_list), 2)
                                    median = int(median) if float(median).is_integer() else median
                                    if title == '{2}':
                                        last_sold = '_{8} ' + str(costs_list[-1])
                                        pattern, median_text = r'/\d+', '/' + str(median)
                                    else:
                                        pattern, median_text = r'\d+/', str(median) + '/'
                                    const[item_id][quality]['cost'] = re.sub(pattern, median_text, cost)
                                text += '{3} ' + str(median) + '_' + \
                                    '{4} ' + str(average) + '_' + \
                                    '{5} ' + str(minimum) + '/' + str(maximum) + '_' + \
                                    '{6} ' + str(cancelled_count) + '_' + \
                                    '{7} ' + str(unsold_count) + '/' + str(len(costs_list) + unsold_count) + \
                                    last_sold
                            const[item_id][quality]['stats'] = text
                    print(datetime.now().timestamp() - stamp, item_id, item_ids.get(item_id), const[item_id])

                new_stats = []
                for item_id, stat in const.items():
                    for quality, values in stat.items():
                        count = db.update_stat(item_id, quality, values)
                        if count <= 0:
                            values.update({
                                'item_id': item_id, 'item_name': item_ids.get(item_id), 'quality': quality})
                            new_stats.append(values)
                db.insert_many('stats', new_stats, primary_key='id', commit=True)
                Auth.dev.printer('конец')
            except IndexError and Exception:
                Auth.dev.thread_except()


def storage_reloader():
    global server
    try:
        Auth.dev.printer('Перезагрузка всей базы лотов')
        db = SQL()
        params_list = {}
        need_hard_handle = []
        db.create_table_lots()
        server.update({'storage_reload': True})
        lot_barrier, calculated_lot_barrier = 1, 1
        client = gspread.service_account(server['json2'])
        spreadsheet_names = [pre + server['storage'] for pre in ['', 'temp-']]
        soup = BeautifulSoup(requests.get(f"{server['link: new_lot_id']}?embed=1").text, 'html.parser')

        if soup.find('div', class_='tgme_widget_message_error') is None:
            raw = str(soup.find('div', class_='tgme_widget_message_text js-message_text')).replace('<br/>', '\n')
            search = re.search(r'(\d+?)/', BeautifulSoup(raw, 'html.parser').get_text(), flags=re.DOTALL)
            lot_barrier = (int(search.group(1)) + 1) if search else lot_barrier

        for storage_spreadsheet in reversed(client.list_spreadsheet_files()):
            if storage_spreadsheet['name'] in spreadsheet_names:
                for worksheet in client.open(storage_spreadsheet['name']).worksheets():
                    lots, stamp = [], datetime.now().timestamp()
                    for raw_lot_text in worksheet.col_values(1):
                        lot = lot_handler.lot_from_raw(raw_lot_text, depth='light')
                        if lot['post_id'] is not None and lot['post_id'] > calculated_lot_barrier:
                            calculated_lot_barrier = lot['post_id']
                        if lot['item_id'] is not None:
                            lots.append(lot)
                            if lot['params'] is not None:
                                if lot['params'] not in params_list:
                                    params_list.update({lot['params']: [lot['item_name']]})
                                else:
                                    if lot['item_name'] not in params_list[lot['params']]:
                                        params_list[lot['params']].append(lot['item_name'])
                        elif lot['post_id'] is not None:
                            need_hard_handle.append(lot)
                    db.insert_many('lots', lots, primary_key='post_id', commit=True)
                    if server['start_message']:
                        start_message = deepcopy(Auth.message(
                            tag=code, old_message=server['start_message'],
                            text=f'\nworksheet-{worksheet.title} {datetime.now().timestamp() - stamp}'))
                        server.update({'start_message': start_message})
                    Auth.dev.printer(f'worksheet-{worksheet.title} {datetime.now().timestamp() - stamp}')
        hard_handled = [lot_handler.hard_item_id_search(lot, params_list) for lot in need_hard_handle]
        db.insert_many('lots', hard_handled, primary_key='post_id', commit=True)

        calculated_lot_barrier += 1
        lot_barrier = (calculated_lot_barrier + 10000) if lot_barrier == 1 else (lot_barrier + 1)
        not_stored_range = range(calculated_lot_barrier, lot_barrier)
        print('DIFF', not_stored_range)
        not_stored = [{'post_id': post_id, 'status': '#active'} for post_id in not_stored_range]
        db.insert_many('lots', not_stored, primary_key='post_id', commit=True)
        server.update({'storage_reload': False})
        db.close()
        if server['start_message']:
            Auth.message(old_message=server['start_message'], text=f'\n{Auth.time()} Reload ended.', tag=code)
    except IndexError and Exception:
        Auth.dev.thread_except()


if __name__ == '__main__' and os.environ.get('server') == 'local':
    import environ
    start(time_now())
    print('Запуск с окружением', environ.environ)
