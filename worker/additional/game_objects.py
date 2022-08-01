import os
import re
import objects
import requests
from time import sleep
from SQL import SQLighter
import concurrent.futures
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
from copy import copy, deepcopy
from objects import bold, code, secure_sql
allowed_lists = {'engrave': ['a', 'w'], 'params': ['a', 'w', 'e']}
symbols = r"[-0-9a-zA-Zа-яА-ЯёЁ\s_{}!#?$%&='*\[\]+.^{}()`⚡|~@:;/\\]"
path = {'lots': 'db/lots.db', 'active': 'db/active.db', 'storage': 'storage.json'}
search_block_pattern = 'initiate conversation with a user|user is deactivated|Have no rights' \
                       '|The group has been migrated|bot was kicked from the supergroup chat' \
                       '|bot was blocked by the user|Chat not found|bot was kicked from the group chat'
properties_title_list = ['au_id', 'lot_id', 'item_emoji', 'enchant', 'engrave', 'item_name', 'params', 'quality',
                         'condition', 'modifiers', 's_castle', 's_emoji', 's_guild', 's_name', 'cost', 'b_castle',
                         'b_emoji', 'b_guild', 'b_name', 'stamp', 'status', 'base']


class Mash:
    def __init__(self, server, const_base):
        self.const_base = const_base
        self.server = server

    @staticmethod
    def create_start_sql_request(table='lots', columns_list=None):
        sql_request = f'INSERT OR REPLACE INTO {table} ('
        if columns_list is None:
            columns_list = properties_title_list
        for column_name in columns_list:
            sql_request += f'{column_name}, '
        return f'{sql_request[:-2]}) VALUES ('

    @staticmethod
    def time(stamp, lang=None):
        day = 0
        text = ''
        if lang is None:
            lang = {'day': '{1}', 'hour': '{2}', 'min': '{3}', 'ends': '{4}'}
        seconds = stamp - objects.time_now()
        hours = int(seconds / (60 * 60))
        if hours > 24:
            day = int(hours / 24)
            hours -= day * 24
            text += f"{day}{lang['day']}{hours}{lang['hour']}"
        elif hours > 0:
            text += f"{hours}{lang['hour']}"
        elif hours < 0:
            hours = 0
        minutes = int((seconds / 60) - (day * 24 * 60) - (hours * 60))
        if minutes >= 0:
            text += f"{minutes}{lang['min']}"
        else:
            text += lang['ends']
        return text

    def get_name_by_base(self, item_name, item_id):
        for const_name in self.const_base:
            if self.const_base[const_name] == item_id:
                item_name = const_name
        return item_name

    def engrave(self, const_name, lot):
        engraved = re.sub(const_name, '', lot['item_name'], 1)
        base = self.const_base.get(const_name)
        if engraved.startswith(' '):
            lot['engrave'] = f'✒{engraved.strip()}'
            lot['item_name'] = const_name
            lot['base'] = str(base)
        if engraved.endswith(' '):
            lot['engrave'] = f'{engraved.strip()}🖋'
            lot['item_name'] = const_name
            lot['base'] = str(base)
        return lot

    def former(self, request, white_list):
        response = {}
        soup = BeautifulSoup(request.text, 'html.parser')
        for post in soup.find_all('div', class_='tgme_widget_message'):
            get_au_id = post.get('data-post')
            if get_au_id:
                au_id = int(re.sub(f"{self.server['channel']}/", '', str(get_au_id)))
                if au_id in white_list:
                    lot_raw = str(post.find('div', class_='tgme_widget_message_text js-message_text'))
                    lot = BeautifulSoup(lot_raw.replace('<br/>', '\n'), 'html.parser').get_text()
                    response[au_id] = f"{au_id}/" + re.sub('/', '&#47;', lot).replace('\n', '/')
        return response

    def detector(self, message, au_post, auth, db_path=path['lots']):
        lot, log_text = None, 'None'
        lot_split = message['text'].split('/')
        print_text = f"{self.server['link: channel']}{lot_split[0]}"
        if int(lot_split[0]) >= au_post:
            db = SQLighter(db_path)
            lot = self.form(message['text'])
            lot_in_db = secure_sql(db.get_lot, lot['au_id'])
            html_link = objects.html_link(print_text, f"№{lot['lot_id']}")
            log_text = f"#Рассылка лота #{lot['lot_id']} {html_link} с айди #{lot['base']} разошелся по "
            log_text += f"{bold('{}')} адресатам " + code(f"id:{lot['au_id']}")
            if lot_in_db is False:
                secure_sql(db.merge, lot)
                if lot['base'] != 'None':
                    if lot['status'] != '#active':
                        print_text += ' Не активен, в базу добавлен'
                else:
                    auth.send_dev_message(print_text + code('\nЭтого куска говна нет в константах'), tag=None)
            else:
                print_text += ' Уже в базе'
        else:
            print_text += ' Старый, lot_updater() разберется'
        objects.printer(print_text)
        return lot, log_text

    def multiple_db_updates(self, lots, lot_updater=True, max_workers=10):
        start_sql_request = self.create_start_sql_request()
        print_text, stamp = f"{len(lots)}: ", datetime.now().timestamp()
        db = {'active': SQLighter(path['active']), 'lots': None if lot_updater else SQLighter(path['lots'])}
        for array in objects.sql_divide(lots):
            sql = {'active': '', 'lots': ''}
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as future_executor:
                futures = [future_executor.submit(self.form, future) for future in array]
                for future in concurrent.futures.as_completed(futures):
                    sql_request = ''
                    lot = future.result()
                    for key in lot:
                        sql_request += f"'{lot.get(key)}', "
                    sql_request = f'{sql_request[:-2]}), ('
                    if lot['status'] == '#active':
                        sql['active'] += sql_request
                    else:
                        sql['lots'] += sql_request
            if lot_updater:
                sql_request = ''
                for key in sql:
                    sql_request += sql[key]
                if sql_request:
                    secure_sql(db['active'].custom_sql, f'{start_sql_request}{sql_request[:-3]};')
            else:
                for key in db:
                    if db[key] and sql[key]:
                        secure_sql(db[key].custom_sql, f'{start_sql_request}{sql[key][:-3]};')
        delay = datetime.now().timestamp() - stamp
        objects.printer(f"{print_text}{delay}")
        return int(delay)

    def form(self, lot_raw, depth='hard'):
        from timer import timer
        split = re.sub('️', '', lot_raw).replace('\'', '&#39;').split('/')
        stamp_now = objects.time_now() - 36 * 60 * 60
        au_id = re.sub(r'\D', '', split[0])
        lot = {}

        for key in properties_title_list:
            lot[key] = 'None'
            if key in ['au_id', 'lot_id', 'cost', 'stamp']:
                lot[key] = 0

        if au_id.isdigit():
            lot['au_id'] = int(au_id)
            for chunk in split:
                for key in self.server['form']:
                    search = re.search(self.server['form'].get(key), chunk)
                    if search:
                        if key == 'title':
                            lot['lot_id'] = int(search.group(1))
                            lot = self.lot_title(lot, search.group(2), depth)
                        elif key == 'condition':
                            lot[key] = re.sub(' ⏰.*', '', search.group(1))
                        elif key == 'modifiers':
                            lot[key] = ''
                        elif key == 'cost':
                            lot[key] = int(search.group(1))
                        elif key in ['seller', 'buyer']:
                            user = search.group(1)
                            search_guild = re.search(r'\[(.*?)]', user)
                            search_castle = re.search(self.server['castle_list'], user)
                            if search_guild:
                                lot[f'{key[0]}_guild'] = search_guild.group(1)
                                user = re.sub(r'\[.*?]', '', user, 1)
                            if search_castle:
                                lot[f'{key[0]}_castle'] = search_castle.group(1)
                                user = re.sub(self.server['castle_list'], '', user, 1)
                            guild_emoji = re.sub(self.server['non_emoji_symbols'], '', user)
                            if len(guild_emoji) > 0:
                                lot[f'{key[0]}_emoji'] = guild_emoji
                                user = re.sub(guild_emoji, '', user)
                            lot[f'{key[0]}_name'] = user.strip()
                        elif key == 'stamp':
                            lot[key] = timer(search)
                        elif key == 'status':
                            status = search.group(1)
                            if status == 'Failed':
                                status = 'Cancelled'
                            if status == '#active':
                                if lot['stamp'] < stamp_now:
                                    status = 'Finished'
                            lot[key] = status
                        else:
                            lot[key] = search.group(1)
                if lot['modifiers'] != 'None' and chunk.startswith(' '):
                    lot['modifiers'] += f'  {chunk.strip()}\n'
            if lot['modifiers'] != 'None' and lot['modifiers'].endswith('\n'):
                lot['modifiers'] = lot['modifiers'][:-1]
        return lot

    def multiple_requests(self, active_array, full_limit, max_workers=10):
        stuck = 0
        loop = True
        ranges = []
        response = {}
        used_array = []
        temp_ranges = []
        update_array = []
        request_array = []
        prev_update_array = []
        limit = copy(full_limit)

        for post_id in active_array:
            ranges.extend(range(post_id - 10, post_id + 11))
        for post_id in dict(sorted(Counter(ranges).items(), key=lambda item: item[1], reverse=True)):
            if post_id not in temp_ranges and post_id in active_array:
                temp_ranges.extend(range(post_id - 10, post_id + 11))
                request_array.append(post_id)

        delay = len(request_array) / 5
        delay = int(delay + 1 if delay.is_integer() is False else delay)

        while loop is True:
            links = []
            if len(update_array) == 0:
                for lot_id in request_array:
                    if len(update_array) < full_limit and lot_id not in used_array:
                        update_array.append(lot_id)
                        used_array.append(lot_id)
            else:
                if update_array == prev_update_array:
                    stuck += 1
                else:
                    prev_update_array = deepcopy(update_array)
                    stuck = 0
                if stuck in [50, 500, 5000]:
                    auth = objects.AuthCentre(os.environ['ERROR-TOKEN'])
                    message = f"active_array({len(active_array)}) = {active_array}\n" \
                              f"request_array({len(request_array)}) = {request_array}\n" \
                              f"update_array({len(update_array)}) = {update_array}\n" \
                              f"delay = {delay}"
                    auth.send_json(message, 'variables', 'Бесконечный цикл обновляющихся лотов')

            for lot_id in update_array:
                links.append(f"{self.server['link: channel']}{lot_id}")
                limit -= 1

            temp_array = deepcopy(update_array)
            print_text, stamp = f"{len(links)}: ", datetime.now().timestamp()
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as future_executor:
                futures = [future_executor.submit(requests.get, future) for future in links]
                for future in concurrent.futures.as_completed(futures):
                    result = self.former(future.result(), active_array)
                    response.update(result)
                    for lot_id in result:
                        if lot_id in temp_array:
                            temp_array[temp_array.index(lot_id)] = None

            update_array = []
            objects.printer(f"{print_text}{datetime.now().timestamp() - stamp}")
            for lot_id in temp_array:
                if lot_id is not None:
                    update_array.append(lot_id)

            if len(update_array) == 0 and len(used_array) == len(request_array):
                loop = False
            if limit <= 0:
                limit = copy(full_limit)
                delay -= 60
                sleep(60)
        return 0 if delay < 0 else delay, list(response.values())

    def lot_title(self, lot, title, depth='hard', generate=False):
        if generate:
            title = objects.html_secure(title)
            title = re.sub('️', '', title).replace('\'', '&#39;')
            for key in properties_title_list:
                lot[key] = 'None'
        item_name = re.sub(r' \+\d+.', '', title)
        enchant_search = re.search(r'\+(\d+) ', item_name)
        for parameter in re.findall(r' \+\d+.', title):
            if lot['params'] == 'None':
                lot['params'] = ''
            lot['params'] += parameter
        if enchant_search:
            lot['enchant'] = enchant_search.group(1)
            item_name = re.sub(r'(\+\d+ )|(⚡)', '', item_name)

        item_emoji = re.sub(self.server['non_emoji_symbols'], '', item_name)
        if len(item_emoji) > 0:
            lot['item_emoji'] = item_emoji
            item_name = re.sub(item_emoji, '', item_name)

        item_name = lot['item_name'] = item_name.strip()
        if item_name in self.const_base:
            lot['base'] = self.const_base[item_name]
            if lot['params'] != 'None' and lot['base'][0] not in allowed_lists['params']:
                lot['base'] = 'None'
        else:
            if re.search(r'lvl\.\d+', lot['item_name']):  # Search mystery items
                if re.search('amulet', lot['item_name']):
                    lot['base'] = 'amt'
                if re.search('ring', lot['item_name']):
                    lot['base'] = 'rng'
                if re.search('totem', lot['item_name']):
                    lot['base'] = 'ttm'

        if lot['params'] != 'None' and lot['base'] == 'None' and depth == 'hard':
            print('драсте')
            allowed = ['params']
            db = SQLighter(path['lots'])
            params_item_names = secure_sql(db.get_dist_base, [lot, allowed])
            if len(params_item_names) > 1:
                allowed = ['params', 'quality']
                params_item_names = secure_sql(db.get_dist_base, [lot, allowed])
                if len(params_item_names) > 1:
                    allowed = ['params', 'quality', 'enchant']
                    params_item_names = secure_sql(db.get_dist_base, [lot, allowed])
            for item_name in params_item_names:
                if item_name in lot['item_name']:
                    lot = self.engrave(item_name, lot)

        if lot['base'] == 'None' and depth == 'hard':
            item_names = []
            for item_name in self.const_base:
                if item_name in lot['item_name'] \
                        and self.const_base[item_name][0] in allowed_lists['engrave']:
                    item_names.append(item_name)
            if len(item_names) >= 1:
                item_name = item_names[0]
                for temp_name in item_names:
                    if temp_name > item_name:
                        item_name = temp_name
                lot = self.engrave(item_name, lot)

        if generate:
            text = ''
            if lot['item_name'] != 'None':
                enchant_emoji = '⚡'
                if lot['item_emoji'] != 'None':
                    text += lot['item_emoji']
                    enchant_emoji = ''
                if lot['enchant'] != 'None':
                    text += bold(f"{enchant_emoji}+{lot['enchant']} ")
                if lot['engrave'] != 'None':
                    engraved = code(re.sub('[✒🖋]', '', lot['engrave']))
                    if lot['engrave'].startswith('✒'):
                        text += f"{bold(lot['item_name'])} {engraved}"
                    else:
                        text += f"{engraved} {bold(lot['item_name'])}"
                else:
                    text += bold(lot['item_name'])
                if lot['params'] != 'None':
                    text += bold(lot['params'])
                if lot['base'] != 'None':
                    text += f" {code('[')}/{lot['base']}{code(']')}"
            if len(text) > 0:
                lot['generate'] = text
        return lot
