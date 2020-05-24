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
    def create_lot(self, array):
        with self.connection:
            self.cursor.execute('INSERT INTO old (au_id, lot_id, enchant, item_name, quality, '
                                'condition, modifiers, seller, cost, buyer, stamp, status) '
                                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (*array,))

    def create_new_lot(self, au_id):
        with self.connection:
            self.cursor.execute('INSERT INTO actives (au_id) VALUES (?)', (au_id,))

    def create_lots(self, sql):
        with self.connection:
            self.cursor.execute(sql)

    def delete_new_lot(self, au_id):
        with self.connection:
            self.cursor.execute('DELETE FROM actives WHERE au_id = ?', (au_id,))

    def get_double(self):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM old WHERE au_id IN '
                                         '(SELECT au_id FROM old GROUP BY au_id HAVING COUNT(*) > 1)').fetchall()
            if result:
                return result
            else:
                return False

    def get_lots(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM old WHERE name = ? ORDER BY stamp', (name,)).fetchall()
        if result:
            return result
        else:
            return False

    def get_quality(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT DISTINCT quality FROM old WHERE name = ?', (name,)).fetchall()
        if result:
            return result
        else:
            return False

    def get_new_au_id(self):
        with self.connection:
            result = self.cursor.execute('SELECT au_id FROM actives').fetchall()
        if result:
            result_array = []
            for i in result:
                result_array.append(i[0])
            return result_array
        else:
            return []

    def get_au_id(self):
        with self.connection:
            result = self.cursor.execute('SELECT au_id FROM old').fetchall()
        if result:
            result_array = []
            for i in result:
                result_array.append(i[0])
            return result_array
        else:
            return []
