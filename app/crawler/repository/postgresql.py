"""Модуль с предварительно настроенным контекстным менеджером"""

import psycopg

from typing import Any, Generator


class Manager:
    """Контекстный менеджер доступа к курсору postgresql"""

    def __init__(self, hostname, port, username, password, database):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def __enter__(self) -> psycopg.Cursor[tuple[Any, ...]]:

        self.conn: psycopg.Connection[tuple[Any, ...]] = psycopg.connect(
            host=self.hostname,
            port=self.port,
            user=self.username,
            password=self.password,
            dbname=self.database,
            autocommit=False,
            isolation_level=psycopg.IsolationLevel.REPEATABLE_READ,
        )

        return self._get_cursor()

    def _get_cursor(self) -> Generator[psycopg.Cursor[tuple[Any, ...]], None, None]:
        try:
            self.cur = self.conn.cursor()
            yield self.cur
        except Exception as e:
            self.conn.rollback()
            self.cur.close()
            self.conn.close()
            raise e

    def __exit__(self):
        self.cur.close()
        self.conn.close()
