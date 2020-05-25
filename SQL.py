# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

    # current_open
    def create_lot(self, values):
        with self.connection:
            self.cursor.execute('INSERT INTO old (au_id, lot_id, enchant, item_name, quality, '
                                'condition, modifiers, seller, cost, buyer, stamp, status) '
                                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (*values,))

    def create_lots(self, sql):
        with self.connection:
            self.cursor.execute(sql)

    def update_lot(self, lot):
        with self.connection:
            self.cursor.execute('UPDATE old SET cost=?, buyer=?, stamp=?, status=? WHERE au_id = ?',
                                (lot['cost'], lot['buyer'], lot['stamp'], lot['status'], lot['au_id'],))

    def get_double(self):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM old WHERE au_id IN '
                                         '(SELECT au_id FROM old GROUP BY au_id HAVING COUNT(*) > 1)').fetchall()
            if result:
                return result
            else:
                return False

    def get_lots(self, item_name):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM old WHERE item_name = ? '
                                         'AND NOT status = ? ORDER BY stamp', (item_name, '#active',)).fetchall()
            result_array = []
            for i in result:
                result_array.append(i)
            return result_array

    def get_quality(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT DISTINCT quality FROM old WHERE item_name = ?', (name,)).fetchall()
            result_array = []
            for i in result:
                result_array.append(i[0])
            return result_array

    def get_active_au_id(self):
        with self.connection:
            result = self.cursor.execute('SELECT au_id FROM old WHERE status = ?', ('#active',)).fetchall()
            result_array = []
            for i in result:
                result_array.append(i[0])
            return result_array

    def get_au_id(self):
        with self.connection:
            result = self.cursor.execute('SELECT au_id FROM old').fetchall()
            result_array = []
            for i in result:
                result_array.append(i[0])
            return result_array
