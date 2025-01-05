# -*- coding: utf-8 -*-
import os
import re
import asyncio
import gspread
import _thread
import requests
from time import sleep
from copy import deepcopy
from aiogram import types
from bs4 import BeautifulSoup
from datetime import datetime
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from telethon.sync import TelegramClient, events

from database.session import engine
from database.models import Base, AllTimeStats, PeriodStats

from functions.SQL import SQL
from functions.lot_handler import LotHandler
from functions.objects import code, time_now, AuthCentre
from functions.initial import const_creation, update_const_items

from services import lot_statistics
# =====================================================================================================================
server = const_creation()
lot_handler = LotHandler(server)
Auth = AuthCentre(GMT=3, ID_DEV=int(os.environ['ID_DEV']), TOKEN=server['DATA_TOKEN'])
bot, dispatcher = Auth.async_bot, Dispatcher(Auth.async_bot)
# =====================================================================================================================


async def update_lots(client: TelegramClient, ids: list) -> None:
    with SQL() as db:
        messages = await client.get_messages(server['auction_channel'], ids=ids)
        for message in messages:
            lot = lot_handler.lot_from_message(message)
            db.update('lots', lot['post_id'], lot, commit=True) if lot.get('post_id') else None
            if lot.get('item_id') is not None and lot.get('status') != '#active':
                item = {'item_id': lot['item_id'], 'quality': lot.get('quality')}
                _thread.start_new_thread(update_stats_records, (item,))


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


def update_stats_records(item: dict):
    try:
        with SQL() as db:
            if item['quality'] is None and db.is_item_has_qualities(item['item_id']):
                item.update({'quality': 'Common'})
            item.update({'item_name': server['item_ids'].get(item['item_id'])})
            lot_statistics.update_statistics(item)
            if item['quality'] is not None:
                item.update({'quality': None})
                lot_statistics.update_statistics(item)
    except IndexError and Exception:
        Auth.dev.executive(None)


def stats_reloader():
    global server
    if server['storage_reload'] is False:
        try:
            dev_message = Auth.message(text=f'{Auth.time()} Stats reload started.', tag=code)
            server.update(update_const_items(gspread.service_account(server['json2']).open('Notify')))
            with SQL() as db:
                lot_counts = db.get_all_lot_counts()
            for item in lot_counts:
                item = dict(item)
                if item['item_id']:
                    update_stats_records(item)
            Auth.message(old_message=dev_message, text=f'\n{Auth.time()} Stats reload ended.', tag=code)
        except IndexError and Exception:
            Auth.dev.thread_except()


@dispatcher.message_handler()
async def message_handler(message: types.Message):
    try:
        if message.chat.id > 0:
            if message.text == '/reload':
                text = 'Перезагружаем базу данных.'
                _thread.start_new_thread(storage_reloader, ())
            elif message.text.startswith('/reload_stats'):
                text = 'Перезагружаем базу статистики.'
                with SQL() as db:
                    try:
                        db.request(f'DROP TABLE {PeriodStats.__table__};')
                    except IndexError and Exception:
                        pass
                    try:
                        db.request(f'DROP TABLE {AllTimeStats.__table__};')
                    except IndexError and Exception:
                        pass
                    db.commit()

                    Base.metadata.create_all(bind=engine, tables=[AllTimeStats.__table__, PeriodStats.__table__])
                    db.commit()
                _thread.start_new_thread(stats_reloader, ())
            else:
                text = 'Бот статистики функционирует в штатном режиме.'
            await bot.send_message(message.chat.id, text, parse_mode='HTML')
    except IndexError and Exception:
        Auth.dev.async_except(message)


def lot_detector():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        client = TelegramClient(os.environ['session1'], int(os.environ['api_id']), os.environ['api_hash'])
        with client:
            @client.on(events.NewMessage(chats=server['auction_channel']))
            @client.on(events.MessageEdited(chats=server['auction_channel']))
            async def post_handler(response):
                if response:
                    lot = lot_handler.lot_from_message(response.message)
                    if lot.get('post_id'):
                        with SQL() as db:
                            db.insert('lots', lot, primary_key='post_id', commit=True)
                    if lot.get('item_id') is not None and lot.get('status') != '#active':
                        item = {'item_id': lot['item_id'], 'quality': lot.get('quality')}
                        _thread.start_new_thread(update_stats_records, (item,))
                    Auth.dev.printer(f'Обновление: {lot}')
            Auth.dev.printer(f"detector() в работе: {server['auction_channel']}")
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
                sleep(1)
                _thread.start_new_thread(lot_telegram_updater, ())
                _thread.exit()


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
        spreadsheet_names = [pre + server['worksheet_storage'] for pre in ['', 'temp-']]
        soup = BeautifulSoup(requests.get(f"{server['link: ID_POST_LOT_UPDATER']}?embed=1").text, 'html.parser')

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


if __name__ == '__main__' and os.environ.get('server') == 'local':
    import environ
    start(time_now())
    print('Запуск с окружением', environ.environ)
