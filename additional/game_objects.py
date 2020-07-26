import re
import requests
from time import sleep
from SQL import SQLighter
import concurrent.futures
from bs4 import BeautifulSoup
from datetime import datetime
from additional.game_time import timer
from additional.objects import bold, code, printer, time_now, secure_sql, html_secure, send_dev_message
db_lots_path = 'db/lots.db'
db_active_path = 'db/active.db'
allowed_params = ['a', 'w', 'e']
allowed_params_engrave = ['a', 'w']
path = {'lots': db_lots_path, 'active': db_active_path, 'storage': 'storage.json'}
properties_title_list = ['au_id', 'lot_id', 'item_emoji', 'enchant', 'engrave', 'item_name', 'params', 'quality',
                         'condition', 'modifiers', 's_castle', 's_emoji', 's_guild', 's_name', 'cost', 'b_castle',
                         'b_emoji', 'b_guild', 'b_name', 'stamp', 'status', 'base', 'raw']


class Mash:
    def __init__(self, server, const_base):
        self.const_base = const_base
        self.server = server

    @staticmethod
    def create_start_sql_request(table='lots', columns_list=None):
        if columns_list is None:
            columns_list = properties_title_list
        start_sql_request = 'INSERT OR REPLACE INTO ' + table + ' ('
        for column_name in columns_list:
            if column_name != 'raw':
                start_sql_request += column_name + ', '
        start_sql_request = start_sql_request[:-2] + ') VALUES ('
        return start_sql_request

    def engrave(self, const_name, lot):
        engraved = re.sub(const_name, '', lot['item_name'], 1)
        base = self.const_base.get(const_name)
        if engraved.startswith(' '):
            lot['engrave'] = '✒' + engraved.strip()
            lot['item_name'] = const_name
            lot['base'] = str(base)
        if engraved.endswith(' '):
            lot['engrave'] = engraved.strip() + '🖋'
            lot['item_name'] = const_name
            lot['base'] = str(base)
        return lot

    def former(self, text):
        response = {'raw': 'False'}
        soup = BeautifulSoup(text, 'html.parser')
        is_post_not_exist = soup.find('div', class_='tgme_widget_message_error')
        if is_post_not_exist is None:
            lot_raw = str(soup.find('div', class_='tgme_widget_message_text js-message_text')).replace('<br/>', '\n')
            get_au_id = soup.find('div', class_='tgme_widget_message_link')
            if get_au_id:
                au_id = re.sub('t.me/.*?/', '', get_au_id.get_text())
                lot = BeautifulSoup(lot_raw, 'html.parser').get_text()
                response = self.form(au_id + '/' + re.sub('/', '&#47;', lot).replace('\n', '/'))
        if is_post_not_exist:
            search_error_requests = re.search('Channel with username .*? not found', is_post_not_exist.get_text())
            if search_error_requests:
                response['raw'] += 'Requests'
        return response

    def multiple_requests(self, global_limit, local_limit, request_array=None, storage=False):
        retry = 0
        loop = True
        used_array = []
        update_array = []
        db = {db_active_path: {'db': SQLighter(db_active_path), 'sql': ''},
              db_lots_path: {'db': SQLighter(db_lots_path) if storage else None, 'sql': ''}}
        start_sql_request = self.create_start_sql_request()
        if request_array is None:
            request_array = secure_sql(db[db_active_path]['db'].get_actives_id)
        if len(request_array) > 0:
            if local_limit / len(request_array) >= 2:
                retry = len(request_array) / 5
                if retry.is_integer() is False:
                    retry += 1
                retry = int(retry)
        while loop is True:
            futures = []
            temp_array = []
            if len(update_array) == 0:
                for au_id in request_array:
                    if len(update_array) < local_limit and au_id not in used_array:
                        update_array.append(au_id)
                        used_array.append(au_id)
            for au_id in update_array:
                futures.append(self.server['link: channel'] + str(au_id) + '?embed=1')
                temp_array.append(au_id)
                local_limit -= 1
            update_array = []
            print_text, stamp = str(len(futures)) + ': ', datetime.now().timestamp()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as future_executor:
                futures = [future_executor.submit(requests.get, future) for future in futures]
                for future in concurrent.futures.as_completed(futures):
                    result = self.former(future.result().content)
                    if result['raw'] != 'FalseRequests' and result['raw'] != 'False':
                        temp_array[temp_array.index(result['au_id'])] = None
                        sql_request_line = ''
                        for lot_property in result:
                            if lot_property != 'raw':
                                sql_request_line += "'" + str(result.get(lot_property)) + "', "
                        sql_request_line = sql_request_line[:-2] + '), ('
                        if result['status'] == '#active':
                            db[db_active_path]['sql'] += sql_request_line
                        else:
                            db[db_lots_path]['sql'] += sql_request_line

            printer(print_text + str(datetime.now().timestamp() - stamp))
            for au_id in temp_array:
                if au_id is not None:
                    update_array.append(au_id)

            if storage:
                for db_path in db:
                    if db[db_path]['db'] and db[db_path]['sql']:
                        sql_request = start_sql_request + db[db_path]['sql'][:-3] + ';'
                        secure_sql(db[db_path]['db'].custom_sql, sql_request)
            else:
                sql_request_line = ''
                for db_path in db:
                    sql_request_line += db[db_path]['sql']
                if sql_request_line:
                    sql_request = start_sql_request + sql_request_line[:-3] + ';'
                    secure_sql(db[db_active_path]['db'].custom_sql, sql_request)

            if len(update_array) == 0 and len(used_array) == len(request_array):
                loop = False
            if local_limit <= 0:
                local_limit = global_limit
                sleep(60)
        sleep(retry)
        return local_limit

    def detector(self, message, au_post, db_path=db_lots_path):
        def log_text_func(link, lot_id, base):
            text = '#Рассылка лота <a href="' + link + '">№' + str(lot_id) + '</a>'
            text += '#' + str(lot_id) + ' с айди #' + base + ' разошелся по '
            text += bold('{}') + ' адресатам'
            return text

        lot, log_text = None, 'None'
        lot_split = message['text'].split('/')
        print_text = self.server['link: channel'] + lot_split[0]
        if int(lot_split[0]) >= au_post:
            db = SQLighter(db_path)
            lot = self.form(message['text'])
            lot_in_db = secure_sql(db.get_lot, lot['au_id'])
            if lot_in_db is False:
                secure_sql(db.merge, lot)
                if lot['base'] != 'None':
                    if lot['status'] == '#active':
                        log_text = log_text_func(print_text, lot['au_id'], lot['base'])
                    else:
                        print_text += ' Не активен, в базу добавлен'
                else:
                    send_dev_message(print_text + '\nЭтого куска говна нет в константах')
            else:
                print_text += ' Уже в базе'
        else:
            print_text += ' Старый, lot_updater() разберется'
        printer(print_text)
        return lot, log_text

    def form(self, lot_raw, depth='hard'):
        stamp_now = time_now() - 36 * 60 * 60
        lot_split = re.sub('\'', '&#39;', re.sub('️', '', lot_raw)).split('/')
        search_au_id = re.search('(\d+)', lot_split[0])
        lot = {}
        for i in properties_title_list:
            lot[i] = 'None'
            if i in ['au_id', 'lot_id', 'cost', 'stamp']:
                lot[i] = 0
        if search_au_id:
            lot['au_id'] = int(search_au_id.group(1))
        for g in lot_split:
            for i in self.server['form']:
                search = re.search(self.server['form'].get(i), g)
                if search:
                    if i == 'title':
                        lot['lot_id'] = int(search.group(1))
                        lot = self.lot_title(lot, search.group(2), depth)
                    elif i == 'condition':
                        lot[i] = re.sub(' ⏰.*', '', search.group(1))
                    elif i == 'modifiers':
                        lot[i] = ''
                    elif i == 'cost':
                        lot[i] = int(search.group(1))
                    elif i in ['seller', 'buyer']:
                        user = search.group(1)
                        search_guild = re.search('\[(.*?)\]', user)
                        search_castle = re.search(self.server['castle_list'], user)
                        if search_guild:
                            lot[i[0] + '_guild'] = search_guild.group(1)
                            user = re.sub('\[.*?\]', '', user, 1)
                        if search_castle:
                            lot[i[0] + '_castle'] = search_castle.group(1)
                            user = re.sub(self.server['castle_list'], '', user, 1)
                        guild_emoji = re.sub(self.server['non_emoji_symbols'], '', user)
                        if len(guild_emoji) > 0:
                            lot[i[0] + '_emoji'] = guild_emoji
                            user = re.sub(guild_emoji, '', user)
                        lot[i[0] + '_name'] = user.strip()
                    elif i == 'stamp':
                        lot[i] = timer(search)
                    elif i == 'status':
                        status = search.group(1)
                        if status == 'Failed':
                            status = 'Cancelled'
                        if status == '#active':
                            if lot['stamp'] < stamp_now:
                                status = 'Finished'
                        lot[i] = status
                    elif i == 'raw':
                        lot[i] = lot
                    else:
                        lot[i] = search.group(1)
            if lot['modifiers'] != 'None' and g.startswith(' '):
                lot['modifiers'] += '  ' + g.strip() + '\n'
        if lot['modifiers'] != 'None' and lot['modifiers'].endswith('\n'):
            lot['modifiers'] = lot['modifiers'][:-1]
        return lot

    def lot_title(self, lot, title, depth='hard', generate=False):
        if generate:
            title = re.sub('\'', '&#39;', title)
            title = re.sub('️', '', title)
            title = html_secure(title)
            for i in properties_title_list:
                lot[i] = 'None'
        params_array = re.findall(' \+\d+.', title)
        item_name = re.sub(' \+\d+.', '', title)
        enchant_search = re.search('\+(\d+) ', item_name)
        for param in params_array:
            if lot['params'] == 'None':
                lot['params'] = ''
            lot['params'] += param
        if enchant_search:
            lot['enchant'] = enchant_search.group(1)
            item_name = re.sub('\+\d+ ', '', item_name)
            item_name = re.sub('⚡', '', item_name)
        item_emoji = re.sub(self.server['non_emoji_symbols'], '', item_name)
        if len(item_emoji) > 0:
            lot['item_emoji'] = item_emoji
            item_name = re.sub(item_emoji, '', item_name)
        item_name = item_name.strip()
        lot['item_name'] = item_name
        if item_name in self.const_base:
            lot['base'] = self.const_base[item_name]
            if lot['params'] != 'None' and lot['base'][0] not in allowed_params:
                lot['base'] = 'None'
        else:
            search_mystery = re.search('lvl\.\d+', lot['item_name'])
            if search_mystery:
                search_amulet = re.search('amulet', lot['item_name'])
                search_ring = re.search('ring', lot['item_name'])
                if search_amulet:
                    lot['base'] = 'amt'
                if search_ring:
                    lot['base'] = 'rng'
        if lot['params'] != 'None' and lot['base'] == 'None' and depth == 'hard':
            allowed = ['params']
            db = SQLighter('db/lots.db')
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
            temp = []
            for item_name in self.const_base:
                if item_name in lot['item_name'] \
                        and self.const_base[item_name][0] in allowed_params_engrave:
                    temp.append(item_name)
            if len(temp) >= 1:
                item_name = temp[0]
                for temp_name in temp:
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
                    text += bold(enchant_emoji + '+' + str(lot['enchant']) + ' ')
                if lot['engrave'] != 'None':
                    engraved = code(re.sub('[✒🖋]', '', lot['engrave']))
                    if lot['engrave'].startswith('✒'):
                        text += bold(lot['item_name']) + ' ' + engraved
                    else:
                        text += engraved + ' ' + bold(lot['item_name'])
                else:
                    text += bold(lot['item_name'])
                if lot['params'] != 'None':
                    text += bold(lot['params'])
                if lot['base'] != 'None':
                    text += ' ' + code('[') + '/' + lot['base'] + code(']')
            if len(text) > 0:
                lot['generate'] = text
        return lot
