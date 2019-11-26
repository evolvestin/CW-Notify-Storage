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
    def create_lot(self, auid, lotid, enchanted, name, quality, castle, seller, cost, buyer, stamp, status):
        with self.connection:
            self.cursor.execute('INSERT INTO old (auid, lotid, enchanted, name, quality, condition, seller, cost, '
                                'buyer, stamp, status) '
                                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                (auid, lotid, enchanted, name, quality, castle, seller, cost, buyer, stamp, status,))

    def create_new_lot(self, auid):
        with self.connection:
            self.cursor.execute('INSERT INTO actives (auid) VALUES (?)', (auid,))

    def create_lots(self, sql):
        with self.connection:
            self.cursor.execute(sql)

    def delete_new_lot(self, auid):
        with self.connection:
            self.cursor.execute('DELETE FROM actives WHERE auid = ?', (auid,))

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

    def get_new_auid(self):
        with self.connection:
            result = self.cursor.execute('SELECT auid FROM actives').fetchall()
        if result:
            return result
        else:
            return False

    def get_auid(self):
        with self.connection:
            result = self.cursor.execute('SELECT auid FROM old').fetchall()
        if result:
            return result
        else:
            return False
