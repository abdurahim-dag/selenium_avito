import re
import time
import psycopg2

from datetime import datetime, timedelta
from logger import logger
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from contextlib import contextmanager
from requestz import Requestz
from downloaderz import Downloaderz
from sites import Sites, Xpaths
from settings import Settings
from typing import Generator, List, Optional


# logging.basicConfig(handlers=[logging.FileHandler('avitospider.log', 'w', 'utf-8')],
#   level=logger.warning,
#   format='%(asctime)s - %(levelname)s - %(message)s')


class Spider:
    def __init__(self, settings: Settings, site_settings: Sites, xpaths: Xpaths):
        self.settings = settings
        self.site_settings = site_settings
        self.xpaths = xpaths


    @contextmanager
    def get_connection(
            self,
    ) -> Generator[psycopg2.extensions.connection, None, None]:
        """ Контекстный менеджер подкючения к БД."""

        conn = psycopg2.connect(
            host=self.settings.db_host,
            port=self.settings.db_port,
            user=self.settings.db_username,
            password=self.settings.db_password,
            dbname=self.settings.db_name
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


    def add_url(self, conn, curs, url, avito_id, table, locality, section_id):
        sql_string = """
            INSERT INTO avito_ad_urls (url,status,avito_id,time_stamp,tablez,locality,section_id) VALUES (%s,%s,%s,%s,%s,%s,%s)
            on conflict do nothing;
        """
        curs.execute(sql_string, (url, 'no', avito_id, str(datetime.now().date()), table, locality, section_id))
        conn.commit()


    def get_table(self, category):
        table = None
        if 'Земельные участки' in category:
            table = "avito_ad_sales_zu"
        elif 'квартир' in category or \
             'Вторичка' in category or \
             'Новостройки' in category or \
             'Комнаты' in category:
            table = "avito_ad_sales_flat"
        elif 'Дома' in category:
            table = "avito_ad_sales_house"
        elif 'Гаражи' in category:
            table = "avito_ad_sales_garage"
        elif 'Коммерческая' in category:
            table = "avito_ad_sales_commercial"
        return table


    def getPage(self, request):
        """Загрузка url.

        request: параметры запроса.
        """
        response = Downloaderz().process_request(request)
        if response == None:
            logger.warning(f"Badd get data ({request.url})")
        return response


    def scroll_shim(self, passed_in_driver, object):
        x = object.location['x']
        y = object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        passed_in_driver.execute_script(scroll_by_coord)
        passed_in_driver.execute_script(scroll_nav_out_of_way)


    def checkOnRetry(func):
        def checkRetry(self, request):
            result = None
            for _ in range(5):
                response = self.getPage(request)
                if response:
                    try:
                        result = func(self, response)
                        if not request.recycle:
                            response["driver"].quit()
                        else:
                            request.url = response["driver"].current_url
                        break
                    except Exception as e:
                        logger.warning(f"{request.url}")
                        logger.warning(f"{str(e)}")
                        if request.driver:
                            request.driver.quit()
                            request.driver = False
                else:
                    logger.warning(f"retry {request.url}")
                    time.sleep(3)
            if response is None:
                raise Exception(f"Не удалось получить страницу {request.url}!")
            return result
        return checkRetry


    @checkOnRetry
    def to_location(self, response):
        driver = response["driver"]
        district = response["request"].district
        url = driver.current_url

        clickable_form = driver.find_element(By.XPATH, self.xpaths.to_search_form)
        clickable_form.clear()
        clickable_button = driver.find_element(By.XPATH, self.xpaths.to_search_button)
        ActionChains(driver) \
            .click(clickable_form) \
            .pause(1) \
            .key_down(Keys.SHIFT) \
            .send_keys(district) \
            .pause(1) \
            .click(clickable_button) \
            .pause(5) \
            .perform()

        if url == driver.current_url:
            raise Exception('Нажатие кнопки след. страницы не привёл к переходу!')


    @checkOnRetry
    def to_find(self, response):
        request = response["request"]
        driver = request.driver
        find = request.params["find"]
        url = driver.current_url

        clickable_form = driver.find_element(By.XPATH, self.xpaths.to_search_form)
        clickable_button = driver.find_element(By.XPATH, self.xpaths.to_search_button)
        clickable_form.clear()
        ActionChains(driver) \
            .click(clickable_form) \
            .pause(1) \
            .key_down(Keys.SHIFT) \
            .send_keys(find) \
            .pause(1) \
            .click(clickable_button) \
            .pause(5) \
            .perform()

        if url == driver.current_url:
            raise Exception('Нажатие кнопки поиска не привёло к переходу!')


    @checkOnRetry
    def to_nedvizh(self, response):
        request = response["request"]
        driver = request.driver

        clickable = driver.find_element(By.XPATH, self.xpaths.to_nedvizh)
        ActionChains(driver) \
            .click(clickable) \
            .pause(5) \
            .perform()

        if 'nedvizhimost' not in driver.current_url:
            raise Exception('Переход на nedvizhimost не состоялся!')


    @checkOnRetry
    def get_categories(self, response):
        request = response["request"]
        driver = request.driver
        urls = []
        categories = driver.find_elements(By.XPATH, self.xpaths.to_category)
        for category in categories:
            name_category = category.text
            category.click()
            time.sleep(5)

            if 'Снять' not in name_category:

                elements = category.find_elements(By.XPATH, self.xpaths.to_categories)

                for element in elements:
                    name_subcategory = element.text
                    if 'снять' in name_subcategory.lower() or 'новостро' in name_subcategory.lower():
                        continue
                    urls += [(element.get_attribute('href'), f"{name_category}-{name_subcategory}")]
        if len(urls) == 0:
            raise Exception(f"Категории не найдены {request.url}!")

        return urls


    def get_ad_urls(self, request):
        urls = []

        while True:

            try:
                urls += self.get_ads(request)
            except:
                logger.critical(f"Не удалось получить ни одного объявленя {request.url}")

            if self.checkNextButton(request):
                try:
                    self.to_next_page(request)
                except:
                    logger.critical(f"Проблемы при переходе к следующей странице {request.url}")
                    break
            else:
                logger.warning(f"Нет более страниц - {request.url}")
                break

        return urls


    @checkOnRetry
    def get_ads(self, response):
        request = response["request"]
        driver = response["driver"]
        elements = driver.find_elements(By.XPATH, self.xpaths.to_ad)

        if len(elements) == 0:
            if not self.checkTextContains(request):
                raise Exception('Нет объявлений!')

        ad_urls = []
        for element in elements:
            ad_urls += [element.get_attribute('href')]
        return ad_urls


    def checkNextButton(self, request):
        try:
            request.driver. \
                find_element(By.XPATH, self.xpaths.to_next_button)
        except:
            return False
        return True


    def checkTextContains(self, request):
        res = False
        try:
            request.driver. \
                find_element(By.XPATH, "//*[contains(text(),'Объявления по вашему запросу в других городах')]")
            res = True
        except:
            pass

        try:
            request.driver. \
                find_element(By.XPATH, "//*[contains(text(),'Похоже на то, что вы ищете')]")
            res = True
        except:
            pass

        try:
            request.driver. \
                find_element(By.XPATH, "//*[contains(text(),'Ничего не найдено в выбранной области поиска')]")
            res = True
        except:
            pass

        return res


    @checkOnRetry
    def to_next_page(self, reponse):
        request = reponse["request"]
        driver = request.driver

        clickable = driver.find_element(By.XPATH, self.xpaths.to_next_button)
        self.scroll_shim(driver, clickable)

        ActionChains(driver) \
            .click(clickable) \
            .pause(5) \
            .perform()

        if request.url == driver.current_url:
            raise Exception('Нажатие кнопки след. страницы не привёл к переходу!')
        # Сохраним новый url в случаи отката.
        request.url = driver.current_url

        logger.warning(f"Следующая страница - {driver.current_url}")


    def start_requests(self):
        date = datetime.now().strftime('%Y-%m-%d')
        with self.get_connection() as conn:
            curs = conn.cursor()

            sql = f"select id from section where time_stamp='{date}'"
            curs.execute(sql)
            conn.commit()
            section_id = curs.fetchone()

            if section_id is None:
                sql_string = "INSERT INTO section (time_stamp,site,status) VALUES (%s,%s,%s) RETURNING id;"
                curs.execute(sql_string, (date, 'avito.ru', "execute"))
                conn.commit()
                section_id = curs.fetchone()[0]

        with open('districts.txt', mode='r', encoding='utf-8') as f:
            district = f.readline()[:-1]
            while district:
                # Начнём со стартовой страницы.
                request = Requestz(
                    url=self.site_settings.start_url,
                    domains=self.settings.domains,
                    recycle=True,
                )

                request.district = district
                self.to_location(request)
                self.to_nedvizh(request)

                request.params["find"] = district
                self.to_find(request)

                categories = self.get_categories(request)

                if categories is None:
                    logger.critical(f"Нет категорий в {request.district} - {request.url}")
                else:
                    for url_category, category in categories:

                        request.url = url_category
                        ad_urls = self.get_ad_urls(request)

                        with self.get_connection() as conn:
                            curs = conn.cursor()
                            for url in ad_urls:
                                avito_id = re.search(
                                    r"_(\d+)$",
                                    url
                                )[1]
                                self.add_url(
                                    conn=conn,
                                    curs=curs,
                                    url=url,
                                    avito_id=avito_id,
                                    locality=district,
                                    table=self.get_table(category),
                                    section_id=section_id
                                )
                            logger.warning(f"Added {len(ad_urls)} urls")
                district = f.readline()[:-1]



            with self.get_connection() as conn:
                curs = conn.cursor()

                sql = f"update section set status='exported' where id='{section_id}'"
                curs.execute(sql)
                conn.commit()
