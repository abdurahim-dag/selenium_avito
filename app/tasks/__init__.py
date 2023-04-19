import logging
import time
from contextlib import contextmanager
from .celery import app
import os
import sys
from .tasks import get_ad
from celery.signals import worker_ready
from celery import group, chord, shared_task, signals
from celery.result import allow_join_result
from typing import Generator, List, Optional
import psycopg2
from psycopg2.extensions import AsIs

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))
from crawler.settings import Settings
from crawler.sites import Xpaths
from crawler.downloaderz import Downloaderz
from crawler.requestz import Requestz



celery = app


@contextmanager
def get_connection(
        host, port, username, password, db
) -> Generator[psycopg2.extensions.connection, None, None]:
    """ Контекстный менеджер подкючения к БД."""

    conn = psycopg2.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        dbname=db
    )

    # Так как у нас скриптовая загрузка состоит из нескольких запросов - insert и select max(update_ts),
    # то откинем все возможные нежданчики.
    conn.autocommit = False
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ)

    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

settings = Settings()
host = settings.db_host
username = settings.db_username
password = settings.db_password
port = settings.db_port
db = settings.db_name

@app.task
def start_task():
    try:
        with get_connection(
            host=host, port=port, username=username, password=password, db=db
        ) as conn:
            curs = conn.cursor()

            while True:
                sql = f"""
                select id, url, tablez, locality, section_id from avito_ad_urls
                where status = 'no'
                LIMIT 1
                """
                curs.execute(sql)
                row = curs.fetchone()
                if row:
                    sql = f"""
                    update avito_ad_urls set status='proceed' where id=%s 
                    """
                    curs.execute(sql, (str(row[0]),))
                    conn.commit()
                    get_ad.apply_async(
                        (row[4], host, port, username, password, db, row[0], row[1], row[2], row[3]),
                        max_retries=4, retry_delay=10, task_kwargs={'retry': True}, countdown=120,
                        time_limit=90,
                    )
                else:
                    logging.warning("Нет объявлений на обработку!")
                    break








        # task_group = group(get_ad.s() for _ in range(20)).apply_async(
        #         priority=255, max_retries=3,
        #         retry_delay=10, task_kwargs={'retry': True},
        #         countdown=5, expires=300
        #     )
        # task_group.get(disable_sync_subtasks=False)
    except:
        logging.critical("Exception on execute tasks!")
    # result_group = task_group.apply_async(
    #     queue='my_queue', routing_key='my_routing_key',
    #     priority=10, max_retries=3,
    #     retry_delay=60, task_kwargs={'retry': True},
    #     countdown=5, expires=3600
    # )
    # with allow_join_result():
    #     result_group.get()





@signals.worker_ready.connect
def on_start(**kwargs):
    start_task.delay()
