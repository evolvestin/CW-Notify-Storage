# -*- coding: utf-8 -*-
import re
import os
import psycopg2
from typing import Union
from environ import environ
from functions.objects import divide
from psycopg2.extras import DictCursor
from sshtunnel import SSHTunnelForwarder
from datetime import datetime, timezone, timedelta

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
lot_integer_columns = ['post_id', 'lot_id', 'enchant', 'price', 'stamp']
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

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
                    if cursor.description and cursor.rowcount:
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
                elif re.search('current transaction is aborted', str(error)):
                    self.connection.rollback()
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

    def is_item_has_qualities(self, item_id: str) -> bool:
        result = self.request(
            f"SELECT * FROM lots WHERE item_id = '{item_id}' AND quality IS NOT NULL LIMIT 1", fetchone=True)
        return True if result else False

    def get_distinct_names_by_params(self, lot: dict, depth: int = 1):
        query = f"SELECT DISTINCT item_name FROM lots WHERE item_id IS NOT NULL AND params = '{lot['params']}'"
        query += f" AND quality = '{lot['quality']}'" if depth in [2, 3] else ''
        query += f" AND enchant = '{lot['enchant']}'" if depth == 3 else ''
        return self.request(query)

    def get_ended_lots_by_item_id(self, item_id: str, quality: str = None) -> list:
        quality_condition = ''
        if quality is not None:
            quality_condition = 'AND quality IS NULL' if quality.lower() == 'common' else f"AND quality = '{quality}'"
        return self.request(f"SELECT * FROM lots WHERE item_id = '{item_id}' {quality_condition} "
                            f"AND NOT status = '#active' ORDER BY stamp")

    def create_table_lots(self) -> None:
        columns = []
        for column in lot_columns:
            integer_format = 'BIGINT' if column in ['stamp'] else 'INTEGER'
            integer_default = 'DEFAULT NULL' if column in ['enchant'] else 'DEFAULT 0 NOT NULL'
            column += f' {integer_format} {integer_default}' if column in lot_integer_columns else ' TEXT NULL'
            columns.append(column)
        columns.append('CONSTRAINT post_id_primary_key PRIMARY KEY (post_id)')
        self.request(f"CREATE TABLE IF NOT EXISTS lots ({', '.join(columns)});")
        self.request(f'CREATE INDEX IF NOT EXISTS index_lot_id ON lots (lot_id);')
        self.request(f'CREATE INDEX IF NOT EXISTS index_item_id ON lots (item_id);')
        self.commit()

    def get_statistics_by_item_id(self, item_id: str, quality: str = None) -> dict:
        queries = {}
        quality_condition = ''
        periods = {'all': None, 'month': 30, 'week': 7}
        now = datetime.now(timezone(timedelta(hours=0)))
        median_percentile = 'PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)'
        if quality is not None:
            quality_condition = 'AND quality IS NULL' if quality.lower() == 'common' else f"AND quality = '{quality}'"

        normal_condition = f"item_id = '{item_id}' {quality_condition} AND NOT status = '#active'"
        sold_condition = f"{normal_condition} AND buyer_castle IS NOT NULL AND NOT status = 'Cancelled'"

        count_select = f"SELECT COUNT(*) FROM lots WHERE {normal_condition}"
        median_price = f'SELECT {median_percentile} AS median_price FROM lots WHERE {sold_condition}'
        absolute_deviation = f"SELECT ABS(price - ({median_price})) AS price, stamp FROM lots WHERE {sold_condition}"

        stats_queries = {
            'count': count_select,
            'median_price': median_price,
            'cancelled': f"{count_select} AND status = 'Cancelled'",
            'sold': f'SELECT COUNT(*) FROM lots WHERE {sold_condition}',
            'average_price': f'SELECT AVG(price) FROM lots WHERE {sold_condition}',
            'minimum_price': f'SELECT MIN(price) FROM lots WHERE {sold_condition}',
            'maximum_price': f'SELECT MAX(price) FROM lots WHERE {sold_condition}',
            'unsold': f"{count_select} AND buyer_castle IS NULL AND NOT status = 'Cancelled'",
            'mad': f'SELECT {median_percentile} AS mad FROM ({absolute_deviation}) AS Q WHERE stamp IS NOT NULL',
        }

        for period, days in periods.items():
            time_ago = (now - timedelta(days=days if days else 0)).timestamp()
            period_condition = f' AND stamp >= {time_ago}' if days else ''
            for key, value in stats_queries.items():
                queries.update({f'{period}_{key}': f'{value}{period_condition}'})
        query = ', '.join([f"COALESCE(({value})::DECIMAL, 0) AS {key}" for key, value in queries.items()])
        result = {period: {} for period in periods}
        for key, value in self.request(f"SELECT {query}", fetchone=True).items():
            for period in periods:
                if key.startswith(f'{period}_'):
                    result[period].update({re.sub(f'{period}_', '', key, 1): value})
        return result
    # ------------------------------------------------------------------------------------------ LOTS END

    # ------------------------------------------------------------------------------------------ STATS BEGIN
    def update_stat(self, item_id: str, quality: str, record: dict, commit: bool = False) -> int:
        quality_condition = f"= '{quality}'" if quality else 'IS NULL'
        result = self.request(
            f"UPDATE stats SET {self.update_items(record)} "
            f"WHERE item_id = '{item_id}' AND quality {quality_condition}", return_row_count=True)
        self.commit() if commit else None
        return result

    def update_statistics_record(self, item_id: str, quality: str, record: dict, commit: bool = False) -> int:
        quality_condition = f"= '{quality}'" if quality else 'IS NULL'
        result = self.request(
            f"UPDATE statistics SET {self.update_items(record)} "
            f"WHERE item_id = '{item_id}' AND quality {quality_condition}", return_row_count=True)
        self.commit() if commit else None
        return result

    def get_all_lot_counts(self):
        stats_count = (
            f"SELECT lot_count FROM statistics WHERE item_id = finder_item_id "
            f"AND COALESCE(quality, 'Common') = COALESCE(finder_quality, 'Common') ORDER BY id DESC LIMIT 1")
        query = (f"SELECT item_id, quality, item_id as finder_item_id, "
                 f"COALESCE(quality, 'Common') AS finder_quality, COUNT(*) AS lot_count "
                 f"FROM lots WHERE NOT status = '#active' GROUP BY item_id, quality")
        return self.request(f"SELECT *, ({stats_count}) AS stats_count FROM ({query}) AS Q")

    def create_table_statistics(self) -> None:
        integer_columns = ['lot_count', 'price']
        columns = ['id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                   '(INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1)']
        for column in ['item_id', 'item_name', 'quality', 'lot_count', 'price', 'stats']:
            number_format = 'NUMERIC(24, 12)' if column in ['price'] else 'INTEGER'
            if column in integer_columns:
                column += f' {number_format} DEFAULT 0 NOT NULL' if column in integer_columns else ' TEXT NULL'
            columns.append(column)
        columns.append('CONSTRAINT id_primary_key PRIMARY KEY (id)')
        self.request(f"CREATE TABLE IF NOT EXISTS statistics ({', '.join(columns)});")
        self.commit()

    def create_table_stats(self) -> None:
        integer_columns = []
        columns = ['id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                   '(INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1)']
        for column in ['item_id', 'item_name', 'quality', 'cost', 'stats']:
            column += f' INTEGER DEFAULT 0 NOT NULL' if column in integer_columns else ' TEXT NULL'
            columns.append(column)
        columns.append('CONSTRAINT stats_pkey PRIMARY KEY (id)')
        self.request(f"CREATE TABLE IF NOT EXISTS stats ({', '.join(columns)});")
        self.commit()
    # ------------------------------------------------------------------------------------------ STATS END
