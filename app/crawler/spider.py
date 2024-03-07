import re
import time
import collections

import psycopg

from .repository.postgresql import Manager
from .sql import avito as sql
from .models import AD_URL, Tables
from downloader import Downloader
from .request import Request

from datetime import datetime, timedelta
from logger import logger

from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from contextlib import contextmanager


from sites import AvitoSite, AvitoXpaths
from settings import Settings
from typing import Generator, List, Optional


# logging.basicConfig(handlers=[logging.FileHandler('avitospider.log', 'w', 'utf-8')],
#   level=logger.warning,
#   format='%(asctime)s - %(levelname)s - %(message)s')


class Spider:
    def __init__(
        self, settings: Settings, site_settings: AvitoSite, xpaths: AvitoXpaths
    ):
        self.settings = settings
        self.site_settings = site_settings
        self.xpaths = xpaths

    def add_url(
        self,
        curs: psycopg.Cursor,
        model: AD_URL,
    ):
        """Вставка ссылки на объявление в БД"""
        curs.execute(sql.insert_ad_urls, params=dict(model))
        curs.connection.commit()

    def get_table(self, category) -> str | None:
        """Получение названия таблицы по названию категории объявления"""
        table = None

        if "Земельные участки" in category:
            table = Tables.zu
        elif (
            "квартир" in category
            or "Вторичка" in category
            or "Новостройки" in category
            or "Комнаты" in category
        ):
            table = Tables.flat
        elif "Дома" in category:
            table = Tables.house
        elif "Гаражи" in category:
            table = Tables.garage
        elif "Коммерческая" in category:
            table = Tables.commercial

        return table

    def getPage(self, request: Request) -> dict:
        """Возврат ответа загрузки страницы по url.

        request: параметры запроса.
        """
        response = Downloader().process_request(request)
        if response is None:
            logger.warning(f"Bad get data ({request.url})")
        return response

    def scroll_shim(self, passed_in_driver: WebDriver, object: WebElement):
        """Скроллинг до элемента"""
        x = object.location["x"]
        y = object.location["y"]
        scroll_by_coord = "window.scrollTo(%s,%s);" % (x, y)
        scroll_nav_out_of_way = "window.scrollBy(0, -120);"
        passed_in_driver.execute_script(scroll_by_coord)
        passed_in_driver.execute_script(scroll_nav_out_of_way)

    def checkOnRetry(func):
        """Декоратор повторных попыток получения ответа загрузки страницы по url"""

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
    def to_location(self, response: dict) -> None:
        """Переход к объявлениям заданного района"""
        driver = response["driver"]
        district = response["request"].district
        url = driver.current_url

        clickable_form = driver.find_element(By.XPATH, self.xpaths.to_search_form)
        clickable_form.clear()
        clickable_button = driver.find_element(By.XPATH, self.xpaths.to_search_button)

        ActionChains(driver).click(clickable_form).pause(1).key_down(
            Keys.SHIFT
        ).send_keys(district).pause(1).click(clickable_button).pause(5).perform()

        if url == driver.current_url:
            raise Exception("Нажатие кнопки поиска не привёл к обновлению страницы!")

    @checkOnRetry
    def to_find(self, response: dict) -> None:
        """Поиск на странице"""
        request = response["request"]
        driver = request.driver
        find = request.params["find"]
        url = driver.current_url

        clickable_form = driver.find_element(By.XPATH, self.xpaths.to_search_form)
        clickable_button = driver.find_element(By.XPATH, self.xpaths.to_search_button)
        clickable_form.clear()

        ActionChains(driver).click(clickable_form).pause(1).key_down(
            Keys.SHIFT
        ).send_keys(find).pause(1).click(clickable_button).pause(5).perform()

        if url == driver.current_url:
            raise Exception("Нажатие кнопки поиска не привело к обновлению страницы!")

    @checkOnRetry
    def to_nedvizh(self, response) -> None:
        """Переход к объявлениям по недвижимости"""
        request = response["request"]
        driver = request.driver

        clickable = driver.find_element(By.XPATH, self.xpaths.to_nedvizh)
        ActionChains(driver).click(clickable).pause(5).perform()

        if "nedvizhimost" not in driver.current_url:
            raise Exception("Переход к объявлениям по недвижимости не состоялся!")

    @checkOnRetry
    def get_categories(self, response):
        """Получение ссылок на страницы объявлений по категориям"""
        request = response["request"]
        driver = request.driver
        urls = []
        categories = driver.find_elements(By.XPATH, self.xpaths.to_category)

        for category in categories:
            name_category = category.text
            category.click()
            time.sleep(5)

            # Аренду пропускаем
            if "Снять" not in name_category:

                sub_categories = category.find_elements(
                    By.XPATH, self.xpaths.to_categories
                )

                for sub_category in sub_categories:
                    name_subcategory = sub_category.text

                    # Аренду пропускаем
                    if (
                        "снять" in name_subcategory.lower()
                        or "новостро" in name_subcategory.lower()
                    ):
                        continue

                    urls += [
                        (
                            sub_category.get_attribute("href"),
                            f"{name_category}-{name_subcategory}",
                        )
                    ]

        if len(urls) == 0:
            raise Exception(f"Категории не найдены {request.url}!")

        return urls

    def get_ad_urls(self, request: Request) -> list:
        """Получения ссылок на объявления со всех страниц"""
        urls = []

        while True:

            try:
                urls += self.get_ads(request)
            except:
                logger.critical(
                    f"Не удалось получить ни одного объявленя {request.url}"
                )

            if self.checkNextButton(request):
                try:
                    self.to_next_page(request)
                except:
                    logger.critical(
                        f"Проблемы при переходе к следующей странице {request.url}"
                    )
                    break
            else:
                logger.warning(f"Нет более страниц - {request.url}")
                break

        return urls

    @checkOnRetry
    def get_ads(self, response) -> list:
        """Получения ссылок на объявления со страницы"""
        request = response["request"]
        driver = response["driver"]
        elements = driver.find_elements(By.XPATH, self.xpaths.to_ad)

        if len(elements) == 0:
            if not self.checkTextContains(request):
                raise Exception("Нет объявлений!")

        ad_urls = []
        for element in elements:
            ad_urls += [element.get_attribute("href")]
        return ad_urls

    def checkNextButton(self, request):
        """Проверка наличия кнопки на переход к след. странице"""
        try:
            request.driver.find_element(By.XPATH, self.xpaths.to_next_button)
        except:
            return False
        return True

    def checkTextContains(self, request):
        """Проверка на корректное содержимое страницы"""
        res = False
        try:
            request.driver.find_element(
                By.XPATH,
                "//*[contains(text(),'Объявления по вашему запросу в других городах')]",
            )
            res = True
        except:
            pass

        try:
            request.driver.find_element(
                By.XPATH, "//*[contains(text(),'Похоже на то, что вы ищете')]"
            )
            res = True
        except:
            pass

        try:
            request.driver.find_element(
                By.XPATH,
                "//*[contains(text(),'Ничего не найдено в выбранной области поиска')]",
            )
            res = True
        except:
            pass

        return res

    @checkOnRetry
    def to_next_page(self, request: Request):
        """Переход к следующей странице"""
        driver = request.driver

        clickable = driver.find_element(By.XPATH, self.xpaths.to_next_button)
        self.scroll_shim(driver, clickable)

        ActionChains(driver).click(clickable).pause(5).perform()

        if request.url == driver.current_url:
            raise Exception("Нажатие кнопки след. страницы не привёл к переходу!")

        # Сохраним новый url в случаи ошибки.
        request.url = driver.current_url

        logger.warning(f"Следующая страница - {driver.current_url}")

    def start(self):
        """Старт"""
        date = datetime.now().strftime("%Y-%m-%d")
        with Manager(
            hostname=self.settings.db_host,
            port=self.settings.db_port,
            username=self.settings.db_username,
            password=self.settings.db_password,
            database=self.settings.db_name,
        ) as curs:

            curs.execute(sql.get_section_by_date, params={"date": date})
            curs.connection.commit()
            section_id = curs.fetchone()

            if section_id is None:
                curs.execute(
                    sql.insert_section,
                    params={
                        "time_stamp": date,
                        "site": "avito.ru",
                        "status": "execute",
                    },
                )
                curs.connection.commit()
                section_id = curs.fetchone()[0]

        with open("districts.txt", mode="r", encoding="utf-8") as f:
            district = f.readline()[:-1]
            while district:
                # Начнём со стартовой страницы.
                request = Request(
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
                    logger.critical(
                        f"Нет категорий в {request.district} - {request.url}"
                    )
                else:
                    for url_category, category in categories:

                        request.url = url_category
                        ad_urls = self.get_ad_urls(request)

                        with Manager(
                            hostname=self.settings.db_host,
                            port=self.settings.db_port,
                            username=self.settings.db_username,
                            password=self.settings.db_password,
                            database=self.settings.db_name,
                        ) as curs:
                            for url in ad_urls:
                                avito_id = re.search(r"_(\d+)$", url)[1]
                                table = self.get_table(category)
                                self.add_url(
                                    curs=curs,
                                    model=AD_URL(
                                        time_stamp=str(datetime.now().date()),
                                        url=url,
                                        avito_id=avito_id,
                                        locality=district,
                                        table=table,
                                        section_id=section_id,
                                    ),
                                )
                            logger.warning(f"Added {len(ad_urls)} urls")
                district = f.readline()[:-1]

            with Manager(
                hostname=self.settings.db_host,
                port=self.settings.db_port,
                username=self.settings.db_username,
                password=self.settings.db_password,
                database=self.settings.db_name,
            ) as curs:
                curs.execute(sql.update_section_status_by_id, params={"id": section_id})
                curs.connection.commit()
