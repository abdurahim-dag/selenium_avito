import logging
import time
import platform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# def PrintException():
#     exc_type, exc_obj, tb = sys.exc_info()
#     f = tb.tb_frame
#     lineno = tb.tb_lineno
#     filename = f.f_code.co_filename
#     linecache.checkcache(filename)
#     line = linecache.getline(filename, lineno, f.f_globals)
#     logging.critical('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


class Downloaderz:


    def __init__(self):
        self.options = Options()
        #self.options.headless = True


    def checkBlock(self, driver):
        if 'blocked' in driver.current_url \
            or 'search' in driver.current_url \
            or driver.page_source is None \
            or 'произошла ошибка' in driver.page_source \
            or '"error":' in driver.page_source \
            or "Доступ ограничен" in driver.page_source:
            return True
        return False


    def get_data(self, request, driver):
        logging.warning(f"Get - {request.url}")
        for _ in range(5):
            try:

                driver.execute_script("window.open('');")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                logging.warning(f"Get data {request.url}")
                driver.get(request.url)
                time.sleep(10)
                logging.warning(f"Get data finish {request.url}")

                if self.checkBlock(driver):
                    logging.warning(f"Banned req({request.url})")
                    time.sleep(10)
                else:
                    break
            except Exception as e:
                logging.warning(str(e))
                logging.warning(f"Bad req({request.url})")


    def process_request(self, request):

        if request.driver:
            driver = request.driver
        else:
            if platform.system() == 'Windows':
                #driver = webdriver.Firefox(options=self.options)
                driver = webdriver.Firefox()
            #service = FirefoxService(executable_path="./geckodriver")
            else:
                driver = webdriver.Remote(
                    command_executor="http://webdriver:4444/wd/hub",
                    options=self.options
                )
            if request.recycle:
                request.driver = driver

        #driver.implicitly_wait(30)

        if request.cookies:
            for domain in request.domains:
                for cookie_name, cookie_value in request.cookies.items():
                    driver.delete_cookie(cookie_name)
                    driver.add_cookie(
                        {
                            'name': cookie_name,
                            'domain': domain,
                            'value': cookie_value
                        }
                    )

        if not request.skip_download:
            self.get_data(request, driver)

        if request.wait_until:
            try:
                WebDriverWait(driver, request.wait_time).until(
                    request.wait_until
                )
            except:
                logging.warning(f"Badd wait_until ({request.url}) ")
                #PrintException()

        if request.script:
            time.sleep(1)
            driver.execute_script(request.script)
            time.sleep(4)

        if self.checkBlock(driver):
            return None

        screenshot = None
        if request.screenshot:
            height = driver.execute_script("return document.body.parentNode.scrollHeight")
            width = driver.execute_script("return document.body.parentNode.scrollWidth")
            driver.set_window_size(width, height)
            screenshot = driver.get_screenshot_as_png()

        return {
            "driver": driver,
            "screenshot": screenshot,
            "request": request
        }
