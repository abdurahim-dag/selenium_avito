import logging
import sys
from selenium.webdriver.common.by import By
from settings import Settings
import datetime
import hashlib
import os
import uuid
import re
import json
import time
from contextlib import contextmanager
#from scanf import scanf
from datetime import datetime, timedelta
from urllib.parse import quote
from typing import Generator, List, Optional
import psycopg2
from psycopg2.extensions import AsIs

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from celery import shared_task
from celery.utils.log import get_task_logger
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded

from sites import Xpaths
from downloaderz import Downloaderz
from requestz import Requestz




# REDIS_HOST = '172.16.0.39'
# REDIS_PORT = '6379'
# REDIS_PASSWORD = ''
# CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/11'
# CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
# CELERY_RESULT_BACKEND = CELERY_BROKER_URL


#app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# app.conf.update(
#     task_soft_time_limit=30,
#     task_time_limit=120,
# )

from PIL import Image
#import pytesseract
import base64
from io import BytesIO
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# def PrintException():
#     exc_type, exc_obj, tb = sys.exc_info()
#     f = tb.tb_frame
#     lineno = tb.tb_lineno
#     filename = f.f_code.co_filename
#     linecache.checkcache(filename)
#     line = linecache.getline(filename, lineno, f.f_globals)
#     logger.critical('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))




class GetAd(object):


    def __init__(self, id, locality, hostname, port, username, password, database, url, table, section_id,\
            path, xpaths):
        self.db_hostname = hostname
        self.db_port = port
        self.db_username = username
        self.db_password = password
        self.db_name = database

        self.adid = id
        self.table = table
        self.url = url
        self.path = path
        self.locality = locality
        self.section_id = section_id

        self.xpaths = xpaths


        #self.profile = webdriver.FirefoxProfile()
        # self.conn = psycopg2.connect(
        #     host=hostname,
        #     port=port,
        #     user=username,
        #     password=password,
        #     dbname=database
        # )
        # self.cur = self.conn.cursor()
        os.makedirs(path, exist_ok=True)


    def getPage(self, request):
        response = Downloaderz().process_request(request)
        if response == None:
            logging.warning(f"Badd get data ({request.url})")
        else:
            response["request"] = request
        logging.warning(f"Get url ({request.url})")
        return response


    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """ Контекстный менеджер подкючения к БД."""

        conn = psycopg2.connect(
            host=self.db_hostname,
            port=self.db_port,
            user=self.db_username,
            password=self.db_password,
            dbname=self.db_name
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


    @contextmanager
    def get_response(self, request):
        while True:
            response = self.getPage(request)
            if response:
                break
            else:
                logging.warning(f"retry {request.url}")
                time.sleep(3)
        try:
            yield response
            response["driver"].quit()
        except Exception as e:
            logging.warning(f"{request.url}")
            logging.warning(f"{str(e)}")
            if request.driver:
                request.driver.quit()
                request.driver = False



    # def ad_status(self, status):
    #     self.cur.execute(f"\
    #         update avito_ad_urls \
    #         set status='{status}' \
    #         where id={self.adid}"
    #     )
    #     self.conn.commit()


    # def __del__(self):
    #     if self.driver:
    #         self.driver.quit()

    def date(self, s):
        if s.find('сегодня') != -1:
            hour, minute = map(int, re.search(r'сегодня в (\d+:\d+)', s)[1].split(':'))
            now = datetime.now()
            day = now.day
            month = now.month
            year = now.year
            return datetime(year, month, day, hour, minute)
        elif s.find('вчера') != -1:
            hour, minute = map(int, re.search(r'вчера в (\d+:\d+)', s)[1].split(':'))
            last_day = datetime.now() - timedelta(days=1)
            day = last_day.day
            month = last_day.month
            year = last_day.year
            return datetime(year, month, day, hour, minute)
        elif re.search(r'.*\d+ \w+ в \d+:\d+.*', s):
            r = re.search(r'\s*(\d+) (\w+) в (\d+):(\d+).*', s)
            day = int(r[1])
            smonth = r[2]
            hour = int(r[3])
            minute = int(r[4])
            monthes = {
                'января': 1,
                'февраля': 2,
                'марта': 3,
                'апреля': 4,
                'майя': 5,
                'июня': 6,
                'июля': 7,
                'августа': 8,
                'сентября': 9,
                'октября': 10,
                'ноября': 11,
                'декабря': 12,
            }
            month = monthes[smonth]
            return datetime(datetime.now().year, month, day, hour, minute)
        else:
            raise Exception(f"Не распознанная дата - {s}")


    # def phoneDemixer(self, e, t):
    #     if len(t) == 0:
    #         return ""
    #     try:
    #         e = int(e)
    #     except:
    #         return ""
    #     o = re.findall("[0-9a-f]+", t)
    #     if e % 2 == 0:
    #         o.reverse()
    #     n = "".join(o)
    #     s = n[::3]
    #     return s


    def check_dublicate(self, avito_id, date):
        with self.get_connection() as conn:
            curs = conn.cursor()
            sql = f"select id from avito_ad_urls where time_stamp='{date}' and avito_id={avito_id}"
            curs.execute(sql)
            conn.commit()
            _id = curs.fetchone()
            if _id is not None:
                return True
        return False

    def start(self):
        print("GO")
        url = self.url

        try:
            request = Requestz(
                url,
                screenshot = True
            )

            with self.get_response(request) as response:

                driver = response['driver']

                avito_id = re.search(
                    r"_(\d+)$",
                    url
                )[1]

                pub_date = driver.find_element(By.XPATH, self.xpaths.to_date).text

                time_stamp = ""
                if pub_date:
                    time_stamp = self.date(pub_date)

                if self.check_dublicate(avito_id, time_stamp):
                    raise Exception(f"Оъявление {avito_id} уже скачено {time_stamp}!")

                name  = driver.find_element(By.XPATH, self.xpaths.to_name).text


                screenshot = response["screenshot"]



                try:
                    address = driver.find_element(By.XPATH, self.xpaths.to_address).text

                except:
                    address = "Без адреса"
                    logging.critical("Без адреса")

                price_value = driver.find_element(By.XPATH, self.xpaths.to_price_value).get_attribute("content")
                price_currency = driver.find_element(By.XPATH, self.xpaths.to_price_currency).get_attribute("content")

                price_original = ''
                for element in driver.find_elements(By.XPATH, self.xpaths.to_price_original):
                    price_original += element.text

                try:
                    x = driver.find_element(By.XPATH, self.xpaths.to_coord).get_attribute("data-map-lat")
                    y = driver.find_element(By.XPATH, self.xpaths.to_coord).get_attribute("data-map-lon")
                except:
                    logging.critical("Error coordinates")

                try:
                    description = driver.find_element(By.XPATH, self.xpaths.to_description).text
                except:
                    description = "Нет описаня"
                    logging.critical("Error description")

                try:
                    other = ''
                    for element in driver.find_elements(By.XPATH, self.xpaths.to_other1):
                        other += element.text
                    other = re.split('\n|;', other)
                except:
                    other = ""
                    logging.critical("Error other1")

                try:
                    other2 = ''
                    for element in driver.find_elements(By.XPATH, self.xpaths.to_other2):
                        other2 += element.text
                    other.append(other2)
                except:
                    logging.critical("Error other2")



                filename = f"{avito_id}.png"
                try:
                    with open(self.path + "\\" + filename, 'wb') as image_file:
                        image_file.write(screenshot)
                except:
                    filename = "ERROR"

                phone = ""

                category = ""
                if other2:
                    category = other2.split('·')[-2]

                other = " | ".join(other)
                other = other.lower() + ' |'

                square_original = re.search(self.xpaths.to_square, other)[1]
                square_value = re.search(r'(\d+[.,]?\d*)', square_original)[1]
                square_currency = re.search(r'\d+[.,]?\d*(.*)', square_original)[1]

                zu_to_city = ""
                house_wall = ""
                house_to_city = ""
                house_square_zu =""
                floor ="0"
                house_type = ""
                house_floors = "0"
                rooms = "0"

                if self.table == 'avito_ad_sales_zu' and other:
                    if re.search(r'расстояние до города:', other):
                        zu_to_city = re.search(r'расстояние до города:\s*(.*?)\s*\|', other)[1]

                if self.table == 'avito_ad_sales_house' and other:
                    if re.search(r'материал стен:', other):
                        house_wall = re.search(r'материал стен:\s*(\w+?)\s*\|', other)[1]
                    if re.search(r'расстояние до города:', other):
                        house_to_city = re.search(r'расстояние до города:\s*(.*?)\s*\|', other)[1]
                    if re.search(r'этажей в доме:', other):
                        house_floors = re.search(r'этажей в доме:\s*(\d+?)\s*\|', other)[1]
                    if re.search(r'площадь участка:', other):
                        house_square_zu = re.search(r'площадь участка:\s*(.*?)\s*\|', other)[1]

                if self.table == 'avito_ad_sales_flat' and other:
                    if re.search(r'этаж:', other):
                        floor = re.search(r'этаж:.*(\d+?).*из.*\d+\s*\|', other)[1]
                        house_floors = re.search(r'этаж:.*\d+.*из.*(\d+?)\s*\|', other)[1]
                    if re.search(r'тип дома:\s*?(\w+)', other):
                        house_type = re.search(r'тип дома:\s*?(\w+)\s*\|', other)[1]
                    if re.search(r'количество комнат:', other):
                        rooms = re.search(r'количество комнат:\s*(\d+?)\s*\|', other)[1]

                with self.get_connection() as conn:
                    self.item_process(
                        conn=conn,
                        item=
                        {
                        "rooms": rooms,
                        "house_floors": house_floors,
                        "house_type": house_type,
                        "floor": floor,
                        "house_square_zu": house_square_zu,
                        "house_to_city": house_to_city,
                        "house_wall": house_wall,
                        "zu_to_city": zu_to_city,
                        "other": other,
                        "category": category,
                        "locality": self.locality,
                        "phone": phone,
                        "time_stamp": time_stamp,
                        "screenshot_file": filename,
                        "avito_id": avito_id,
                        "url": url,
                        "description": description,
                        "square_currency": square_currency,
                        "square_value": square_value,
                        "square_original": square_original,
                        "table": self.table,
                        "x": x,
                        "y": y,
                        "price_original": price_original,
                        "price_currency": price_currency,
                        "price_value": price_value,
                        "address": address,
                        "name": name,
                        "section_id": self.section_id
                    })
                    logging.critical(f"OK: {url}")

            result = "ok"
        except Exception as e:
            driver.quit()
            logging.critical(f"Exception on: {url}")
            logging.critical(f"{str(e)}")
            #PrintException()
            result = "no"

        return result

        # phone_id = re.search(
        #     r"avito.item.phone.+'(.+)';",
        #     self.driver.find_element_by_xpath(self.xpaths["to_id"]
        # ).get_attribute('innerText')).group(1)

        # if phone_id:
        #     pkey = self.phoneDemixer(avito_id,phone_id)
        #     url_tel = f"https://www.avito.ru/items/phone/{avito_id}?pkey={pkey}&retina=1&vsrc=r"
        #     request = Requestz(
        #         url_tel,
        #         script="""
        #             document.evaluate("//a[contains(@id,'rawdata-tab')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();
        #         """,
        #         driver=self.driver,
        #         recycle=True
        #         )
        #
        #     response = None
        #     while response == None:
        #         logger.critical(f"Get AD ({url})")
        #         response = Downloaderz().process_request(request)
        #     self.driver = response['driver']
        #
        #     body = str.encode(self.driver.find_element_by_xpath("//pre").text)
        #     phone = self.get_phone(body)

        # try:
        #     square_original = driver.find_element_by_xpath(self.xpaths[to_square]).text
        # except:
        #     square_original = driver.find_element_by_xpath(self.xpaths[to_square+'_alter']).text
        # square_value = re.search(r'(\d+[.,]?\d*)', square_original).group(1)
        # square_currency = re.search(r'\d+[.,]?\d*(.*)', square_original).group(1)

    # def get_phone(self, body):
    #     telephone = ""
    #     try:
    #         image64 = json.loads(body)
    #         im = Image.open(BytesIO(base64.b64decode(image64["image64"][22:].encode())))
    #         telephone = pytesseract.image_to_string(im)
    #     except:
    #         logger.critical("Error telephone")
    #         PrintException()
    #     return telephone


    def item_process(self, conn, item):
        curs = conn.cursor()
        if item.get('table','') == 'avito_ad_sales_flat':
            curs.execute("""
                insert into %s
                (name, address, price_value, price_currency,
                price_original, x, y, square_value,
                square_currency, square_original, description, other,
                url, screenshot_file, time_stamp, avito_id,
                phone, floor, house_floors, house_type,
                rooms, section_id, category, locality)
                values(%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s)
                on conflict do nothing;
                """,(AsIs(item.get('table','')),
                item.get('name','')[:199],item.get('address','')[:199],item.get('price_value','0'),item.get('price_currency','')[:49],
                item.get('price_original','')[:199],item.get('x','0'),item.get('y','0'),item.get('square_value','0'),
                item.get('square_currency','').replace(';','')[:49],item.get('square_original','')[:49],item.get('description',''),item.get('other',''),
                item.get('url','')[:499],item.get('screenshot_file','')[:199],item.get('time_stamp','2000-01-01 00:00:00.057463'),item.get('avito_id','0'),
                item.get('phone','')[:99],item.get('floor','0'),item.get('house_floors','0'),item.get('house_type','')[:99],
                item.get('rooms','0'),item.get('section_id', ''),item.get('category','')[:99],item.get('locality','')[:99]))
        elif item.get('table','') == 'avito_ad_sales_house':
            curs.execute("""
                insert into %s
                (name, address, price_value, price_currency,
                price_original, x, y, square_value,
                square_currency, square_original, description, other,
                url, screenshot_file, time_stamp, avito_id,
                phone, section_id, category, locality,
                wall, to_city, floors, square_zu)
                values(%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s)
                on conflict do nothing;
                """ ,(AsIs(item.get('table','')),
                item.get('name','')[:49],item.get('address','')[:199],item.get('price_value','0'),item.get('price_currency','')[:49],
                item.get('price_original','')[:199],item.get('x','0'),item.get('y','0'),item.get('square_value','0'),
                item.get('square_currency','').replace(';','')[:49],item.get('square_original','')[:49],item.get('description',''),item.get('other',''),
                item.get('url','')[:499],item.get('screenshot_file','')[:199],item.get('time_stamp','2000-01-01 00:00:00.057463'),item.get('avito_id','0'),
                item.get('phone','')[:99],item.get('section_id', ''),item.get('category','')[:99],item.get('locality','')[:99],
                item.get('house_wall','')[:99],item.get('house_to_city','')[:99],item.get('house_floors','0'),item.get('house_square_zu','')[:99]))
        elif item.get('table','') == 'avito_ad_sales_zu':
            curs.execute("""
                insert into %s
                (name, address, price_value, price_currency,
                price_original, x, y, square_value,
                square_currency, square_original, description, other,
                url, screenshot_file, time_stamp, avito_id,
                phone, section_id, category, locality,
                to_city)
                values(%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s)
                on conflict do nothing;
                """ ,(AsIs(item.get('table','')),
                item.get('name','')[:199],item.get('address','')[:199],item.get('price_value','0'),item.get('price_currency','')[:49],
                item.get('price_original','')[:199],item.get('x','0'),item.get('y','0'),item.get('square_value','0'),
                item.get('square_currency','').replace(';','')[:49],item.get('square_original','')[:49],item.get('description',''),item.get('other',''),
                item.get('url','')[:499],item.get('screenshot_file','')[:199],item.get('time_stamp','2000-01-01 00:00:00.057463'),item.get('avito_id','0'),
                item.get('phone','')[:99],item.get('section_id', ''),item.get('category','')[:99],item.get('locality','')[:99],
                item.get('zu_to_city','')[:99]))
        else:
            curs.execute("""
                insert into %s
                (name, address, price_value, price_currency,
                price_original, x, y, square_value,
                square_currency, square_original, description, other,
                url, screenshot_file, time_stamp, avito_id,
                phone, section_id, category, locality)
                values(%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s)
                on conflict do nothing;
                """ ,(AsIs(item.get('table','')),
                item.get('name','')[:199],item.get('address','')[:199],item.get('price_value','0'),item.get('price_currency','')[:49],
                item.get('price_original','')[:199],item.get('x','0'),item.get('y','0'),item.get('square_value','0'),
                item.get('square_currency','').replace(';','')[:49],item.get('square_original','')[:49],item.get('description',''),item.get('other',''),
                item.get('url','')[:499],item.get('screenshot_file','')[:199],item.get('time_stamp','2000-01-01 00:00:00.057463'),item.get('avito_id','0'),
                item.get('phone','')[:99],item.get('section_id', ''),item.get('category','')[:99],item.get('locality','')[:99]))
        conn.commit()



@shared_task
def get_ad( id, locality, hostname, username, password, database, url, table, section_id, path):
    try:
        ad = GetAd( id, locality, hostname, username, password, database, url, table, section_id, path, Xpaths() )
        result = ad.start()
    except SoftTimeLimitExceeded:
        logging.critical(f"Time out for {url}")
        result = "time out"
    return result


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

from multiprocessing import Process
section_id = sys.argv[1]

with get_connection(
 host=host, port=port, username=username, password=password, db=db
) as conn:
    curs = conn.cursor()

    sql = f"""
        select id, url, tablez, locality from avito_ad_urls where section_id={section_id}
        where status = 'no'
        LIMIT 1
        """
    curs.execute(sql)
    row = curs.fetchone()
    if row:
        sql = f"""
        update avito_ad_urls set status='proceed' where id=%s 
        """
        curs.execute(sql, (row[0]))
        conn.commit()

if row:
    proc = GetAd(
        hostname=host, port=port, username=username, password=password, database=db,
        id=row[0], url=row[1], table=row[2], locality=row[3],
        section_id=section_id, path=f"./{section_id}",
        xpaths=Xpaths()
    )
    res = proc.start()
    if res == 'ok':
        sql = f"update avito_ad_urls set status='{res}' where id={row[0]}"
        curs.execute(sql)
        conn.commit()


