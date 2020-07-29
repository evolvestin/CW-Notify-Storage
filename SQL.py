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

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

    def merge(self, dictionary):
        table = 'lots'
        if dictionary.get('username'):
            dictionary['updates'] = 1
            table = 'users'
        start_sql_request = 'INSERT OR REPLACE INTO ' + table
        sql_request_line = ' ('
        for i in dictionary:
            if i != 'raw':
                sql_request_line += i + ', '
        sql_request_line = sql_request_line[:-2] + ') VALUES ('
        for i in dictionary:
            if i != 'raw':
                sql_request_line += "'" + str(dictionary.get(i)) + "', "
        sql_request_line = sql_request_line[:-2] + ');'
        with self.connection:
            self.cursor.execute(start_sql_request + sql_request_line)

    def custom_sql(self, sql):
        with self.connection:
            self.cursor.execute(sql)

    def get_item(self, base):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM actives WHERE base = ? ORDER BY stamp', (base,)).fetchall()
        if result:
            return result
        else:
            return False

    def get_parameter(self, params):
        with self.connection:
            result = self.cursor.execute("SELECT DISTINCT enchant, condition, params FROM lots "
                                         "WHERE item_name = ? "
                                         "AND quality = ? "
                                         "AND NOT condition = 'Broken' AND NOT params = 'None'"
                                         "ORDER BY enchant DESC", (params[0], params[1],)).fetchall()
        result_array = []
        for i in result:
            result_array.append(i)
        return result_array

    def get_actives(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE status = '#active' ORDER BY stamp").fetchall()
        result_array = []
        for i in result:
            result_array.append(i)
        return result_array

    def get_not_actives_by_base(self, base):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE base = ? "
                                         "AND NOT status = '#active' ORDER BY stamp", (base,)).fetchall()
            result_array = []
            for i in result:
                result_array.append(i)
            return result_array

    def get_updates(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE updates = 1;")
        result_array = []
        for i in result:
            result_array.append(i)
        return result_array

    def get_dist_base(self, array):
        start_sql_request = "SELECT DISTINCT item_name FROM lots WHERE base <> 'None' "
        sql_request_line = ''
        allowed = array[1]
        lot = array[0]
        for i in lot:
            if i in allowed:
                sql_request_line += 'AND ' + i + " = '" + str(lot.get(i)) + "' "
        sql_request_line = sql_request_line[:-1] + ';'
        with self.connection:
            result = self.cursor.execute(start_sql_request + sql_request_line)
        result_array = []
        for result_lot in result:
            if result_lot['item_name'] in lot['item_name']:
                result_array.append(result_lot['item_name'])
        return result_array

    def get_actives_id(self):
        with self.connection:
            result = self.cursor.execute("SELECT au_id FROM lots WHERE status = '#active'")
        result_array = []
        for i in result:
            result_array.append(i['au_id'])
        return result_array

    def get_not_actives(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE NOT status = '#active' ORDER BY stamp")
        result_array = []
        for i in result:
            result_array.append(i)
        return result_array

    def get_all_au_id(self):
        with self.connection:
            result = self.cursor.execute("SELECT au_id FROM lots")
        result_array = []
        for i in result:
            result_array.append(i['au_id'])
        return result_array

    def get_dist_quality(self, lower=False):
        with self.connection:
            result = self.cursor.execute("SELECT DISTINCT quality FROM lots "
                                         "WHERE NOT quality = 'None' AND NOT quality = ''").fetchall()
        result_array = [i['quality'] for i in result]
        result_array.insert(0, 'Common')
        if lower:
            result_array = [i.lower() for i in result_array]
        return result_array

    def get_dist_quality_by_base(self, base):
        with self.connection:
            result = self.cursor.execute("SELECT DISTINCT quality FROM lots WHERE base = ? "
                                         "AND NOT quality = 'None' AND NOT quality = ''", (base,)).fetchall()
        result_array = []
        for i in result:
            result_array.append(i['quality'])
        if len(result_array) > 0:
            result_array.insert(0, 'Common')
        return result_array

    def get_user_subs(self, item_id):
        with self.connection:
            result = self.cursor.execute("SELECT id, lang, gmt, subscriptions FROM users WHERE "
                                         "subscriptions LIKE '%" + item_id + "%' AND NOT blocked = '🅾️';")
        result_array = []
        for i in result:
            result_array.append(i)
        return result_array

    def get_active_by_base(self, base):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE base = ? "
                                         "AND status = '#active' ORDER BY stamp", (base,)).fetchall()
        result_array = []
        for i in result:
            result_array.append(i)
        return result_array

    def get_user(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
        if result:
            return result[0]
        else:
            return False

    def get_lot(self, au_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE au_id = ?", (au_id,)).fetchall()
        if result:
            return result[0]
        else:
            return False

    def get_by_lot_id(self, lot_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM lots WHERE lot_id = ?", (lot_id,)).fetchall()
        if result:
            return result[0]
        else:
            return False

    def update_updates(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET updates='0' WHERE id = ?", (user_id,))

    def update_blocked(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET blocked='🅾️', updates=1 WHERE id = ?", (user_id,))
