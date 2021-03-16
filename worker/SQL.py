# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:
    def __init__(self, database):
        def dict_factory(cursor, row):
            dictionary = {}
            for idx, col in enumerate(cursor.description):
                dictionary[col[0]] = row[idx]
            return dictionary
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()

    def custom_sql(self, sql):
        with self.connection:
            r = self.cursor.execute(sql)
            for lot in r:
                print(lot)

    def merge(self, dictionary):
        sql_request = f'INSERT OR REPLACE INTO lots '
        for key in dictionary:
            sql_request += f'{key}, '
        sql_request = f'({sql_request[:-2]}) VALUES ('
        for key in dictionary:
            sql_request += f"'{dictionary.get(key)}', "
        with self.connection:
            self.cursor.execute(f'{sql_request[:-2]});')

    def get_all_au_id(self):
        with self.connection:
            result = self.cursor.execute("SELECT au_id FROM lots")
        result_array = []
        for lot in result:
            result_array.append(lot['au_id'])
        return result_array

    def get_actives_id(self):
        with self.connection:
            result = self.cursor.execute("SELECT au_id FROM lots WHERE status = '#active'")
        result_array = []
        for lot in result:
            result_array.append(lot['au_id'])
        return result_array

    def get_lot(self, au_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE au_id = ?", (au_id,)).fetchall()
        if result:
            return result[0]
        else:
            return False

    def get_ended_lots(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE NOT status = '#active' ORDER BY stamp")
        result_array = []
        for lot in result:
            result_array.append(lot)
        return result_array

    def get_not_actives_by_base(self, base):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE base = ? "
                                         "AND NOT status = '#active' ORDER BY stamp", (base,)).fetchall()
            result_array = []
            for lot in result:
                result_array.append(lot)
            return result_array

    def get_dist_quality(self, lower=False):
        with self.connection:
            result = self.cursor.execute("SELECT DISTINCT quality FROM lots "
                                         "WHERE NOT quality = 'None' AND NOT quality = ''").fetchall()
        result_array = [lot['quality'] for lot in result]
        result_array.insert(0, 'Common')
        if lower:
            result_array = [i.lower() for i in result_array]
        return result_array

    def get_dist_base(self, array):
        sql_request = "SELECT DISTINCT item_name FROM lots WHERE base <> 'None' "
        result_array = []
        lot = array[0]
        for key in lot:
            if key in array[1]:
                sql_request += f"AND {key} = '{lot.get(key)}' "
        with self.connection:
            result = self.cursor.execute(f'{sql_request[:-1]};')
        for result_lot in result:
            if result_lot['item_name'] in lot['item_name']:
                result_array.append(result_lot['item_name'])
        return result_array
