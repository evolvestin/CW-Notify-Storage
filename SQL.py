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
            self.cursor.execute('INSERT INTO old (auid, lotid, enchanted, name, quality, castle, seller, cost, '
                                'buyer, stamp, status) '
                                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                (auid, lotid, enchanted, name, quality, castle, seller, cost, buyer, stamp, status,))

    def create_lots(self, sqls):
        with self.connection:
            self.cursor.execute(sqls)

    def update_users(self, id, usernick, fullscore, score, lasttime, updates):
        with self.connection:
            self.cursor.execute('UPDATE users SET usernick=?, fullscore=?, score=?, lasttime=?, updates=? WHERE id = ?',
                                (usernick, fullscore, score, lasttime, updates, id,))

    def get_lot(self, id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM actives WHERE id = ?', (id,)).fetchall()
        if result:
            return result[0]
        else:
            return False

    def get_lots(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM old WHERE name = ? ORDER BY stamp', (name,)).fetchall()
        if result:
            return result
        else:
            return False