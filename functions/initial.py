# -*- coding: utf-8 -*-
import os
import re
import gspread
import concurrent.futures
from ast import literal_eval
from settings import base_dir
from functions.SQL import SQL
from functions.GDrive import Drive
from functions.lot_constants import raw_symbols
from functions.objects import t_me, sub_blank, environmental_files


def update_const_items(spreadsheet: gspread.models.Spreadsheet, name: str = 'items2', dimension: str = 'ROWS'):
    emojis, long_emojis = [], []
    allowed_to = {'params': [], 'engrave': []}
    item_ids, item_names, item_tiers = {}, {}, {}
    data = spreadsheet.worksheet(name).get('A1:Z50000', major_dimension=dimension)
    keys = [key.lower().strip() for key in data.pop(0)]
    for row in data:
        item_id, item_name = row[1].strip(), sub_blank(row[0]).replace('\'', '&#39;')
        item_ids.update({item_id: item_name}), item_names.update({item_name: item_id})
        emoji = re.sub(raw_symbols, '', item_name)
        emojis.append(emoji) if emoji not in emojis and len(emoji) == 1 else None
        long_emojis.append(emoji) if emoji not in long_emojis and len(emoji) > 1 else None
        for key, value in zip(keys, row):
            if key == 'tier':
                tier = re.sub(r'[\w\s]', '', sub_blank(value))
                item_tiers.update({item_id: tier}) if tier else None
            elif key in ['params', 'engrave'] and value.strip():
                allowed_to[key].append(item_name)
    symbols = raw_symbols.format(''.join(emojis), '{}')
    symbols += f"|{'|'.join(long_emojis)}" if len(long_emojis) > 0 else ''
    return {
        'symbols': symbols,
        'item_ids': item_ids,
        'allowed_to': allowed_to,
        'item_names': item_names,
        'item_tiers': item_tiers,
    }


def const_creation() -> dict:
    server = {}
    for file_name in environmental_files(base_dir.joinpath('.'), python=True):
        search_json = re.search(r'(\d)\.json', file_name)
        server.update({f'json{search_json.group(1)}': base_dir.joinpath(file_name)}) if search_json else None

    server.update({
        'storage_reload': False,
        'spreadsheet': gspread.service_account(server['json2']).open('Notify'),
    })

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as future_executor:
        futures = []
        for name, dimension in [
                ('database', ''), ('sessions', server['json2']), ('items2', 'ROWS'), ('resources', 'COLUMNS')]:
            futures.append(future_executor.submit(get_sheet_data, server['spreadsheet'], name, dimension))
        for future in concurrent.futures.as_completed(futures):
            server.update(future.result())
    return server


def get_sheet_data(spreadsheet: gspread.models.Spreadsheet, name: str, dimension: str = 'ROWS') -> dict:
    server = {}

    title = 'pages' if name.startswith('pages') else name
    title = 'items' if name.startswith('items') else title

    if title == 'items':
        server.update(update_const_items(spreadsheet, name, dimension))

    elif title == 'database':
        with SQL() as db:
            db.create_table_lots(), db.create_table_stats()

    elif title == 'sessions':
        client = Drive(dimension)
        for file in client.files():
            if file['name'] in [f"{os.environ['session1']}.session", f"{os.environ['session2']}.session"]:
                client.download_file(file['id'], file['name'])

    elif title == 'resources':
        data = spreadsheet.worksheet(name).get('A1:Z50000', major_dimension=dimension)
        keys = data.pop(0)
        for resource in data:
            if resource[0] == os.environ['server']:
                for key, value in zip(keys, resource):
                    if key == 'form':
                        server.update({key: literal_eval(sub_blank(value))})
                    elif key == 'auction_channel':
                        server.update({key: value, f'link: {key}': f'{t_me}s/{value}/'})
                    elif key == 'lot_updater_post_id':
                        server.update({key: int(value), f'link: {key}': f'{t_me}lot_updater/{value}'})
                    else:
                        server.update({key: value})
    return server
