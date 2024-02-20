# -*- coding: utf-8 -*-
import re
import os
import psycopg2
from typing import Union
from environ import environ
from functions.objects import divide
from psycopg2.extras import DictCursor
from sshtunnel import SSHTunnelForwarder

if environ == 'local':
    print('POSTGRESQL через SSH')
    tunnel = SSHTunnelForwarder((os.environ['SSH_HOST'], int(os.environ['SSH_PORT'])),
                                remote_bind_address=('127.0.0.1', 5432),
                                ssh_username=os.environ['SSH_USER'],
                                ssh_password=os.environ['SSH_PASS'])
    tunnel.start()
    postgresql_port = tunnel.local_bind_port
else:
    print('POSTGRESQL без SSH')
    postgresql_port = 5432


commit_query = True  # Произойдет ли коммит в базу в любой точке (глобально)
lot_integer_columns = ['post_id', 'lot_id', 'price', 'stamp']
lot_columns = ['post_id',
               'lot_id', 'item_id', 'item_name', 'item_emoji', 'enchant', 'left_engrave', 'right_engrave',
               'params', 'quality', 'condition', 'modifiers', 'seller_castle', 'seller_emoji', 'seller_guild',
               'seller_name', 'price', 'buyer_castle', 'buyer_emoji', 'buyer_guild', 'buyer_name', 'stamp', 'status']


def perform_connection():
    connection = psycopg2.connect(
        port=postgresql_port,
        cursor_factory=DictCursor,
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        database=os.environ['DB_NAME'],
        host=os.environ.get('DB_HOST') or '127.0.0.1',
    )
    connection.autocommit = False
    return connection


class SQL:
    def __init__(self):
        connected = False
        while connected is False:
            try:
                self.connection = perform_connection()
                connected = True
            except IndexError and Exception:
                connected = False

    # ------------------------------------------------------------------------------------------ UTILITY BEGIN
    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit() if commit_query else None

    def request(self, sql: str, fetchone: bool = False, return_row_count: bool = False):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                if return_row_count is False:
                    if cursor.description:
                        return dict(cursor.fetchone()) if fetchone else list(cursor.fetchall())
                    else:
                        return None
                else:
                    return cursor.rowcount
            except IndexError and Exception as error:
                if re.search('Software caused connection abort', str(error)):
                    print('БЫЛА ОШИБКА, ПРОПУСТИЛИ')
                    self.connection = perform_connection()
                    return self.request(sql, fetchone, return_row_count)
                else:
                    raise error

    @staticmethod
    def insert_items(record: dict) -> tuple:
        """Преобразование dict в строки - keys и values (только для INSERT)"""
        values = []
        for key, value in record.items():
            if value is None:
                values.append('NULL')
            elif type(value) is dict:
                values.append(f'"{value}"')
            else:
                values.append(f"'{value}'")
        return ', '.join(record.keys()), ', '.join(values)

    @staticmethod
    def update_items(record: dict) -> str:
        """Преобразование dict в строку key=value, key=value ... (только для UPDATE)"""
        items = []
        for key, value in record.items():
            if value is None:
                value = 'NULL'
            elif type(value) is dict:
                value = f'"{value}"'
            elif type(value) is list and len(value) == 1 and type(value[0]) is str:
                value = value[0]
            else:
                value = f"'{value}'"
            items.append(f'{key}={value}')
        return ', '.join(items)
    # ------------------------------------------------------------------------------------------ UTILITY END

    # ------------------------------------------------------------------------------------------ STANDARD BEGIN
    def insert(self, table: str, record: dict, primary_key: str = 'post_id', commit: bool = False) -> int:
        """
        :param table: table name
        :param record: record dict
        :param primary_key: replace data by unique column with ON CONFLICT
        :param commit: commit changes if needed
        :return:
        """
        keys, values = self.insert_items(record)
        result = self.request(
            f"INSERT INTO {table} ({keys}) VALUES ({values}) ON CONFLICT({primary_key}) "
            f"DO UPDATE SET {', '.join([f'{key} = EXCLUDED.{key}' for key in record.keys()])}", return_row_count=True)
        self.commit() if commit else None
        return result

    def update(self, table: str, item_id: Union[int, str],
               record: dict, primary_key: str = 'post_id', commit: bool = False) -> None:
        """
        :param table: table name
        :param item_id: update record with that primary_key
        :param record: record dict
        :param primary_key: name of column with primary_key
        :param commit: commit changes if needed
        :return:
        """
        result = self.request(
            f"UPDATE {table} SET {self.update_items(record)} WHERE {primary_key} = '{item_id}'", return_row_count=True)
        self.commit() if commit else None
        return result

    def insert_many(self, table: str, records: list, primary_key: str = 'post_id', commit: bool = False) -> int:
        """
        :param table: table name
        :param records: records list
        :param primary_key: replace data by unique column with ON CONFLICT
        :param commit: commit changes if needed
        :return:
        """
        counter = 0
        if len(records) > 0:
            keys, _ = self.insert_items(records[0])
            on_conflict = ', '.join([f'{key} = EXCLUDED.{key}' for key in records[0].keys()])
            for part_records in divide(records, sep=100000):
                part_array = []
                for record in part_records:
                    _, values = self.insert_items(record)
                    part_array.append(f'({values})')
                counter += self.request(
                    f"INSERT INTO {table} ({keys}) VALUES {', '.join(part_array)} "
                    f"ON CONFLICT({primary_key}) DO UPDATE SET {on_conflict}", return_row_count=True)
        self.commit() if commit else None
        return counter
    # ------------------------------------------------------------------------------------------ STANDARD END

    # ------------------------------------------------------------------------------------------ LOTS BEGIN
    def get_active_lots(self) -> list:
        return self.request("SELECT * FROM lots WHERE status = '#active'")

    def get_distinct_qualities(self) -> list:
        result = self.request("SELECT DISTINCT quality FROM lots WHERE NOT quality = ''")
        return [record['quality'] for record in list(result)]

    def get_ended_lots_by_item_id(self, item_id) -> list:
        query = f"SELECT * FROM lots WHERE NOT status = '#active' AND item_id = '{item_id}' ORDER BY stamp"
        return self.request(query)

    def get_distinct_names_by_params(self, lot: dict, depth: int = 1):
        query = f"SELECT DISTINCT item_name FROM lots WHERE item_id IS NOT NULL AND params = '{lot['params']}'"
        query += f" AND quality = '{lot['quality']}'" if depth in [2, 3] else ''
        query += f" AND enchant = '{lot['enchant']}'" if depth == 3 else ''
        return self.request(query)

    def create_table_lots(self) -> None:
        columns = []
        for column in lot_columns:
            integer_format = 'BIGINT' if column in ['stamp'] else 'INTEGER'
            column += f' {integer_format} DEFAULT 0 NOT NULL' if column in lot_integer_columns else ' TEXT NULL'
            columns.append(column)
        columns.append('CONSTRAINT lots_pkey PRIMARY KEY (post_id)')
        self.request(f"CREATE TABLE IF NOT EXISTS lots ({', '.join(columns)});")
        self.commit()
    # ------------------------------------------------------------------------------------------ LOTS END

    # ------------------------------------------------------------------------------------------ STATS BEGIN
    def update_stat(self, item_id: str, quality: str, record: dict, commit: bool = False) -> int:
        quality_condition = "= '{quality}'" if quality else 'IS NULL'
        result = self.request(
            f"UPDATE stats SET {self.update_items(record)} "
            f"WHERE item_id = '{item_id}' AND quality {quality_condition}", return_row_count=True)
        self.commit() if commit else None
        return result

    def create_table_stats(self) -> None:
        integer_columns = []
        columns = ['id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                   '(INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1)']
        for column in ['item_id', 'item_name', 'quality', 'cost', 'stats']:
            integer_format = 'BIGINT' if column in ['stamp'] else 'INTEGER'
            column += f' {integer_format} DEFAULT 0 NOT NULL' if column in integer_columns else ' TEXT NULL'
            columns.append(column)
        columns.append('CONSTRAINT stats_pkey PRIMARY KEY (id)')
        self.request(f"CREATE TABLE IF NOT EXISTS stats ({', '.join(columns)});")
        self.commit()
    # ------------------------------------------------------------------------------------------ STATS END
