# -*- coding: utf-8 -*-
import os
import re
import json
import asyncio
import gspread
import _thread
import requests
from time import sleep
from copy import deepcopy
from aiogram import types
from decimal import Decimal
from statistics import mean
from bs4 import BeautifulSoup
from datetime import datetime
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from statistics import median as median_function
from telethon.sync import TelegramClient, events

from functions.SQL import SQL, commit_query
from functions.lot_handler import LotHandler
from functions.objects import code, bold, time_now, AuthCentre
from functions.initial import const_creation, update_const_items
# =====================================================================================================================
server = const_creation()
lot_handler = LotHandler(server)
Auth = AuthCentre(GMT=3, ID_DEV=int(os.environ['ID_DEV']), TOKEN=server['DATA_TOKEN'])
bot, dispatcher = Auth.async_bot, Dispatcher(Auth.async_bot)
# =====================================================================================================================


async def update_lots(client: TelegramClient, ids: list) -> None:
    with SQL() as db:
        messages = await client.get_messages(server['channel'], ids=ids)
        for message in messages:
            lot = lot_handler.lot_from_message(message)
            db.update('lots', lot['post_id'], lot, commit=True) if lot.get('post_id') else None
            if lot.get('item_id') is not None and lot.get('status') != '#active':
                item = {'item_id': lot['item_id'], 'quality': lot.get('status')}
                _thread.start_new_thread(update_stats_records, (db, item))


def start(stamp):
    global server
    if os.environ.get('server') == 'local':
        threads = []
    else:
        Auth.dev.start(stamp)
        threads = [lot_detector, lot_telegram_updater]
    for thread_element in threads:
        _thread.start_new_thread(thread_element, ())
    executor.start_polling(dispatcher)


def update_stats_records(db: SQL, item: dict):
    try:
        if item['quality'] is None and db.is_item_has_qualities(item['item_id']):
            item.update({'quality': 'Common'})
        create_stats(db, item)
        update_statistics(db, item)
        if item['quality'] is not None:
            item.update({'quality': None})
            create_stats(db, item)
            update_statistics(db, item)
    except IndexError and Exception:
        Auth.dev.executive(None)


@dispatcher.message_handler()
async def message_handler(message: types.Message):
    try:
        if message.chat.id > 0:
            if message.text == '/reload':
                text = 'Перезагружаем базу данных.'
                _thread.start_new_thread(storage_reloader, ())
            elif message.text == '/reload_stats':
                text = 'Перезагружаем базу статистики.'
                _thread.start_new_thread(stats_reloader, ())
            else:
                text = 'Бот статистики функционирует в штатном режиме.'
            await bot.send_message(message.chat.id, text, parse_mode='HTML')
    except IndexError and Exception:
        Auth.dev.async_except(message)


def update_statistics(db: SQL, item: dict) -> None:
    stats = db.get_statistics_by_item_id(item['item_id'], item['quality'])
    week, month, all_time = stats.get('week', {}), stats.get('month', {}), stats.get('all', {})

    price = all_time.get('median_price', 0)
    price = month.get('median_price', 0) if month.get('sold', 0) >= 16 else price
    price = week.get('median_price', 0) if week.get('sold', 0) >= 8 else price

    value = {
        'price': price,
        'stats': str(json.dumps(stats, default=str)),
        'lot_count': stats.get('all', {}).get('count', 0),
        'item_name': server['item_ids'].get(item['item_id']),
    }
    if db.update_statistics_record(item['item_id'], item['quality'], value, commit=commit_query) == 0:
        value.update({'item_id': item['item_id'], 'quality': item['quality']})
        db.insert('statistics', value, primary_key='id', commit=commit_query)


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
                    with SQL() as db:
                        if lot.get('post_id'):
                            db.insert('lots', lot, primary_key='post_id', commit=True)
                        if lot.get('item_id') is not None and lot.get('status') != '#active':
                            item = {'item_id': lot['item_id'], 'quality': lot.get('status')}
                            _thread.start_new_thread(update_stats_records, (db, item))
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
            with SQL() as db:
                ids = [lot['post_id'] for lot in db.get_active_lots()]
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


def stats_reloader():
    global server
    if server['storage_reload'] is False:
        try:
            stamp = datetime.now().timestamp()
            dev_message = Auth.message(text=f'{Auth.time()} Stats reload started.', tag=code)
            server.update(update_const_items(gspread.service_account(server['json2']).open('Notify')))
            with SQL() as db:
                db.request('DROP TABLE stats;')
                db.request('DROP TABLE statistics;')
                db.commit()
                db.create_table_stats()
                db.create_table_statistics()
                db.commit()

                dev_message = deepcopy(Auth.message(
                    tag=code, old_message=dev_message,
                    text=f'\nRecreated tables {datetime.now().timestamp() - stamp}'))

                for item in db.get_all_lot_counts():
                    if item['item_id'] and item['lot_count'] != item['stats_count']:
                        update_stats_records(db, dict(item))
            Auth.message(old_message=dev_message, text=f'\n{Auth.time()} Stats reload ended.', tag=code)
        except IndexError and Exception:
            Auth.dev.thread_except()


def storage_reloader():
    global server
    try:
        Auth.dev.printer('Перезагрузка всей базы лотов')
        server = const_creation()
        server.update({'storage_reload': True})
        dev_message = Auth.message(text=f'{Auth.time()} Reload started.', tag=code)

        db = SQL()
        params_list = {}
        need_hard_handle = []
        lot_barrier, calculated_lot_barrier = 1, 1
        client = gspread.service_account(server['json2'])
        spreadsheet_names = [pre + server['storage'] for pre in ['', 'temp-']]
        soup = BeautifulSoup(requests.get(f"{server['link: lot_updater_post_id']}?embed=1").text, 'html.parser')

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
                    dev_message = deepcopy(Auth.message(
                        tag=code, old_message=dev_message,
                        text=f'\nworksheet-{worksheet.title} {datetime.now().timestamp() - stamp}'))
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
        Auth.message(old_message=dev_message, text=f'\n{Auth.time()} Reload ended.', tag=code)
    except IndexError and Exception:
        Auth.dev.thread_except()


def create_stats(db: SQL, item: dict) -> None:
    time_week = time_now() - (7 * 24 * 60 * 60)
    lots = db.get_ended_lots_by_item_id(item['item_id'], item['quality'])
    stats = {'costs_list_full': [], 'costs_list_week': [],
             'unsold_count_full': 0, 'unsold_count_week': 0,
             'cancelled_count_full': 0, 'cancelled_count_week': 0}
    for lot in lots:
        if lot['status'] != 'Cancelled':
            if lot['buyer_castle'] is not None:
                stats['costs_list_full'].append(lot['price'])
                if lot['stamp'] >= time_week:
                    stats['costs_list_week'].append(lot['price'])
            else:
                stats['unsold_count_full'] += 1
                if lot['stamp'] >= time_week:
                    stats['unsold_count_week'] += 1
        else:
            stats['cancelled_count_full'] += 1
            if lot['stamp'] >= time_week:
                stats['cancelled_count_week'] += 1

    value = {'cost': '0/0', 'stats': ''}
    costs_list_full = stats['costs_list_full']
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
            unsold_count = stats['unsold_count_full']
            cancelled_count = stats['cancelled_count_full']
        else:
            costs_list = stats['costs_list_week']
            unsold_count = stats['unsold_count_week']
            cancelled_count = stats['cancelled_count_week']
        if len(costs_list) > 0:
            minimum = min(costs_list)
            maximum = max(costs_list)
            cost = value['cost']
            median = median_function(costs_list)
            average = round(mean(costs_list), 2)
            median = int(median) if float(median).is_integer() else median
            if title == '{2}':
                last_sold = '_{8} ' + str(costs_list[-1])
                pattern, median_text = r'/\d+', '/' + str(median)
            else:
                pattern, median_text = r'\d+/', str(median) + '/'
            value['cost'] = re.sub(pattern, median_text, cost)
        text += '{3} ' + str(median) + '_' + \
                '{4} ' + str(average) + '_' + \
                '{5} ' + str(minimum) + '/' + str(maximum) + '_' + \
                '{6} ' + str(cancelled_count) + '_' + \
                '{7} ' + str(unsold_count) + '/' + str(len(costs_list) + unsold_count) + \
                last_sold
        value['stats'] = text

    if db.update_stat(item['item_id'], item['quality'], value) == 0:
        value.update({
            'item_id': item['item_id'],
            'quality': item['quality'],
            'item_name': server['item_ids'].get(item['item_id'])
        })
        db.insert('stats', value, primary_key='id')
        print(f"CREATED {item['item_id']} {item['quality']}", time_now(iso=True))
    else:
        print(f"UPDATED {item['item_id']} {item['quality']}", time_now(iso=True))


if __name__ == '__main__' and os.environ.get('server') == 'local':
    import environ
    start(time_now())
    print('Запуск с окружением', environ.environ)
