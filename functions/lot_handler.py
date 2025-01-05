import os
import re
from datetime import datetime
from functions.objects import sub_blank
from functions.lot_constants import cyrillic_modifiers
from game_time_converter import convert_game_date_to_timestamp
from functions.SQL import SQL, lot_columns, lot_integer_columns


class LotHandler:
    def __init__(self, server: dict):
        self.symbols: str = server['symbols']
        self.lot_pattern: dict = server['form']
        self.allowed_to: dict = server['allowed_to']
        self.item_names: dict = server['item_names']
        self.castle_emojis: str = server['castle_pattern']

    def lot_from_message(self, message) -> dict:
        if message and message.id and message.message:
            return self.lot_from_raw(f"{message.id}/{re.sub('/', '&#47;', message.message)}".replace('\n', '/'))
        return {}

    def engrave(self, lot: dict, item_name: str) -> dict:
        modified = re.sub(item_name, '{ITEM_NAME}', lot['item_name'], 1)
        if '{ITEM_NAME}' in modified:
            update = {'item_id': self.item_names[item_name], 'item_name': item_name}
            if modified.endswith('{ITEM_NAME}'):
                update.update({'left_engrave': re.sub(r'\{ITEM_NAME}', '', modified).strip()})
            elif modified.startswith('{ITEM_NAME}'):
                update.update({'right_engrave': re.sub(r'\{ITEM_NAME}', '', modified).strip()})
            elif modified != '{ITEM_NAME}':
                engraves = [part.strip() for part in modified.split('{ITEM_NAME}')]
                update.update({'left_engrave': engraves[0]})
                update.update({'right_engrave': engraves[1]}) if len(engraves) > 1 else None
            lot.update(update)
        return lot

    def hard_item_id_search(self, lot: dict, all_lot_params: dict = None) -> dict:
        if lot['item_id'] is None:
            if all_lot_params is not None:  # Search by params (in all_lot_params)
                for item_name in all_lot_params.get(lot['params'], []):
                    if item_name in lot['item_name']:
                        lot = self.engrave(lot, item_name)
                        break
            else:  # Search by params (in database)
                names = []
                with SQL() as db:
                    params_item_names = db.get_distinct_names_by_params(lot, depth=1)
                    if len(params_item_names) > 1:
                        params_item_names = db.get_distinct_names_by_params(lot, depth=2)
                        if len(params_item_names) > 1:
                            params_item_names = db.get_distinct_names_by_params(lot, depth=3)
                for record in params_item_names:
                    names.append(record['item_name']) if record['item_name'] in lot['item_name'] else None
                if len(names) >= 1:
                    lot = self.engrave(lot, str(sorted(names, key=len, reverse=True)[0]))

        if lot['item_id'] is None and lot['item_name'] is not None:
            names = []
            for item_name in self.item_names:
                if item_name in lot['item_name'] and item_name in self.allowed_to.get('engrave', []):
                    names.append(item_name)
            if len(names) >= 1:
                lot = self.engrave(lot, str(sorted(names, key=len, reverse=True)[0]))
        return lot

    def search_lot_title(self, lot: dict, title: str):
        item_name = re.sub(r' \+\d+.', '', title)
        enchant_search = re.search(r'\+(\d+) ', item_name)
        for parameter in re.findall(r' \+\d+.', title):
            if lot.get('params') is None:
                lot.update({'params': ''})
            lot['params'] += parameter

        if enchant_search:
            lot.update({'enchant': int(enchant_search.group(1))})
            item_name = re.sub(r'(\+\d+ )|(⚡)', '', item_name)
        else:
            lot.update({'enchant': None})
            item_name = re.sub(r'⚡', '', item_name)

        item_emoji = re.sub(self.symbols, '', item_name)
        if len(item_emoji) > 0:
            lot.update({'item_emoji': item_emoji})
            item_name = re.sub(item_emoji, '', item_name)

        lot.update({'item_name': item_name.strip()})
        if lot['item_name'] in self.item_names:
            lot.update({'item_id': self.item_names[lot['item_name']]})
            if lot.get('params') is not None and lot['item_name'] not in self.allowed_to.get('params', []):
                lot.update({'item_id': None})
        else:
            if re.search(r'lvl\.\d+', lot['item_name']):  # Search mystery items
                if re.search('amulet', lot['item_name']):
                    lot.update({'item_id': 'amt'})
                elif re.search('ring', lot['item_name']):
                    lot.update({'item_id': 'rng'})
                elif re.search('[Tt]otem', lot['item_name']):
                    lot.update({'item_id': 'ttm'})
        return lot

    def lot_from_raw(self, raw_lot_text: str, depth: str = 'hard') -> dict:
        lot = {}
        now = int(datetime.now().timestamp()) - 36 * 60 * 60
        line = sub_blank(raw_lot_text).replace('\'', '&#39;')
        [lot.update({key: 0 if key in lot_integer_columns else None}) for key in lot_columns]
        post_id_search = re.search(r'(\d+?)/', line)
        if post_id_search:
            lot.update({'post_id': int(post_id_search.group(1))})
            for key, pattern in self.lot_pattern.items():
                search = re.search(pattern, line)
                if search:
                    if key == 'date':
                        lot.update({key: convert_game_date_to_timestamp(search.group(1), os.environ['server'])})
                    elif key == 'price':
                        lot.update({key: int(search.group(1))})
                    elif key == 'condition':
                        lot.update({key: re.sub(' ⏰.*', '', search.group(1))})
                    elif key == 'quality':
                        lot.update({key: search.group(1) if search.group(1) else None})
                    elif key == 'title':
                        lot.update({'lot_id': int(search.group(1))})
                        lot = self.search_lot_title(lot, search.group(2))
                    elif key == 'status':
                        status = 'Cancelled' if search.group(1) == 'Failed' else search.group(1)
                        lot.update({key: 'Finished' if status == '#active' and lot['stamp'] < now else status})
                    elif key == 'modifiers':
                        lot_modifiers = search.group(1)
                        if re.search('[а-яА-Я]', lot_modifiers):
                            for cyrillic_modifier, real_modifier in cyrillic_modifiers.items():
                                if cyrillic_modifier in lot_modifiers:
                                    lot_modifiers = re.sub(cyrillic_modifier, real_modifier, lot_modifiers)
                        lot.update({key: re.sub('/', '\n', lot_modifiers)})
                    elif key in ['seller', 'buyer']:
                        name = search.group(1)
                        guild_search = re.search(r'\[(.*?)]', name)
                        castle_search = re.search(self.castle_emojis, name)
                        if guild_search:
                            name = re.sub(r'\[.*?]', '', name, 1)
                            lot.update({f'{key}_guild': guild_search.group(1)})
                        if castle_search:
                            name = re.sub(self.castle_emojis, '', name, 1)
                            lot.update({f'{key}_castle': castle_search.group(1)})
                        guild_emoji = re.sub(self.symbols, '', name)
                        if len(guild_emoji) > 0:
                            name = re.sub(guild_emoji, '', name)
                            lot.update({f'{key}_emoji': guild_emoji})
                        if name.strip() and name.strip() != 'None':
                            lot.update({f'{key}_name': name.strip()})
                    else:
                        lot.update({key: search.group(1)})
            lot = self.hard_item_id_search(lot) if depth == 'hard' else lot
        return lot
