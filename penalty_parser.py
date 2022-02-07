"""
-----------------------------------------------------------------

  В модуле хранится парсер

-----------------------------------------------------------------

  Классы и функции:

  BotParser - парсер
  get_data - интерфейс для взаимодейсвтия с парсером

------------------------------------------------------------------
"""

# импорты с питонячих библиотек
import datetime
import time
import uuid
from pathlib import Path
from time import sleep
from random import choice

# импорты со стронних библиотек
# from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (NoSuchElementException,
                                        ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        TimeoutException, )

# Ожидания
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from fake_useragent import UserAgent
from seleniumwire import webdriver

# импорт с локальных модулей
# from settings import URL_FINES as URL
# from settings import PROXY_PATH, PROXY_TYPE, PROXY_API
# from utils.loggers import parser_logger
# from utils.work_with_proxy import read_proxy_json
from loggers import parser_logger

URL = 'https://гибдд.рф/check/fines#++'

URL_Refresh = 'https://гибдд.рф/check/fines'
is_screen = False


class BotParserPenalty:
    """  Бот-парсер вся логика парсера лежит тут """

    def __init__(self, available_proxy=None):

        """
        Инициализация данных, где:

         * gov_number - государственный номер автомобиля.
         * sts - номер свидетельства о регистрации.
        """
        self.sts_number = None
        self.gov_number = None
        self.parses_uuid = uuid.uuid4()
        self.busy = False

        # юзер агент и прокси
        user_agent = UserAgent().firefox
        # if available_proxy is None:
        #     self.proxy_list = read_proxy_json(PROXY_PATH, PROXY_TYPE, PROXY_API)
        #     self.proxy = choice(self.proxy_list)
        # else:
        #     self.proxy = available_proxy

        extensions_path = str(Path().parent.absolute().parent.absolute()) + '/gibdd_parser/gibdd_parser/firefox_addons/'  # заменить
        # extensions_path = './firefox_addons/'
        options = webdriver.FirefoxOptions()
        # options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        # options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.headless = True

        # настройки для seleniumwire
        sw_options = {
            # 'proxy': {
            #     'http': self.proxy,
            #     'https': self.proxy.replace('http', 'https')
            # },
            'user-agent': {
                user_agent,
            },
        }

        self.driver = webdriver.Firefox(options=options, seleniumwire_options=sw_options)
        self.driver.install_addon(f'{extensions_path}ublock_origin.xpi', )
        self.driver.set_page_load_timeout(40)
        # self.driver.implicitly_wait(5)

        self.driver.set_window_size(1200, 1200)
        self.driver.get(URL)
        parser_logger.info(f"[INIT] END {self.parses_uuid=}")

    def __parse_result(self) -> list:

        """ Парсит результат """
        xpath_not_found = '//*[@id="checkFines"]/p[contains(@class, "check-space check-message")]/p'

        parser_logger.info('[PR] Начало парсинга результата')
        start = time.time()

        # Пытаемся как можно быстрее узнать результат
        while (time.time() - start) < 4:
            try:
                WebDriverWait(self.driver, 0.2).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//*[@id="checkFines"]/div/ul/li/span')
                    )
                )
                parser_logger.info('[PR] Найдены штрафы')
                result = []
                fine_blocs = self.driver.find_elements_by_class_name('finesItem')
                for block in fine_blocs:
                    inner_result = []
                    all_li = block.find_elements_by_tag_name('li')
                    for li in all_li:
                        # Крутимся пока не прогрузится текст
                        start_search_text = time.time()
                        # Устанавливаем лимит на ожидания текса в одну секунду
                        # TODO убрать велосипед
                        while (time.time() - start_search_text) < 1:
                            inner_data = li.find_elements_by_tag_name('span')
                            if len(inner_data[0].text) > 0 and len(inner_data[1].text) > 0:
                                parser_logger.info(f'[PR] Найдены данные {inner_data[0].text}:{inner_data[1].text}')
                                break
                        inner_result.append({'name': inner_data[0].text, 'value': inner_data[1].text})
                    result.append(inner_result)

                parser_logger.info(f'[PR] Конец парсинга')

                return result
            except TimeoutException:
                pass

            try:
                elem = WebDriverWait(self.driver, 0.2).until(
                    EC.presence_of_element_located((By.XPATH, xpath_not_found))
                )
                return elem.text
            except TimeoutException:
                pass
        parser_logger.info('[PR] Таймаут парсинга результата')
        raise TimeoutException
        # Ждем пока появится элементы
        # ([string-length(text()) > 1] - не работает и все равно находит без текста)

    def __input_values_and_click_button(self) -> None:

        """ Вводит обязательные поля и нажимает на кнопку поиска """

        number = self.gov_number[:6]
        region = self.gov_number[6:]
        parser_logger.info('[IC] Ввод полей')

        try:
            parser_logger.info(f'[IC] Поле гос. номера {self.parses_uuid=}')
            # sleep(5)
            number_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "checkFinesRegnum"))
            )
            # number_field = self.driver.find_element_by_id('checkFinesRegnum')
            number_field.send_keys(number)
        except TimeoutException:
            parser_logger.warning('Бесконечная загрузка')
            load_message = self.driver.find_element_by_xpath('//*[contains(text(), "Идет загрузка")]')
            if is_screen:
                self.driver.save_screenshot('find_erros.jpeg')
            if load_message:
                parser_logger.warning('Сохранен скриншот')
                raise TimeoutException

        # sleep(2)
        parser_logger.info(f'[IC] Поле региона {self.parses_uuid=}')
        # region_field = self.driver.find_element_by_id('checkFinesRegreg')
        region_field = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.ID, "checkFinesRegreg"))
        )
        region_field.send_keys(region)


        # sleep(2)
        parser_logger.info(f'[IC] Поле свидетельства о регистрации {self.parses_uuid=}')
        # sts_field = self.driver.find_element_by_id('checkFinesStsnum')
        sts_field = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.ID, "checkFinesStsnum")))
        sts_field.send_keys(self.sts_number)

        # sleep(2)
        parser_logger.info(f'[IC] Нажатие на кнопку поиска {self.parses_uuid=}')
        # search_button = self.driver. \
        #     find_element_by_xpath('//*[contains(text(), "запросить проверку")]')
        if is_screen:
            self.driver.save_screenshot(f'button{datetime.datetime.now()}.png')
        search_button = WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "запросить проверку")]')))

        parser_logger.info(f'[IC] Найдена кнопка поиска {str(search_button)}')
        # self.driver.save_screenshot('button.png')
        ActionChains(self.driver).move_to_element(search_button).click().perform()
        # ActionChains(self.driver).click(search_button).perform()

    def parse_data(self, gov_number, sts) -> list:
        self.busy = True
        self.gov_number = gov_number
        self.sts_number = sts
        parser_logger.info(f"[INIT] GOV_NUM: {gov_number}, STS: {sts} {self.parses_uuid=}")
        """ Парсит штрафы """
        from time import time as ttime

        time_start = ttime()
        self.__input_values_and_click_button()
        result = self.__parse_result()

        parser_logger.info(f"[PD] Конец парсинга. Возврат значения {result=}")
        if result is str:
            result = [result]
        elif not result:
            result.append('not found')

        self.make_screenshot('return_result')
        # result.append({"name": "time spend on parsing", "value": str(ttime()-time_start)})
        # parser_logger.info(f"[PD] Конец парсинга. Возврат значения {result=}")
        self.busy = False
        return result

    def __del__(self):

        """ При удалении экземпляра класса закрывает соединение с selenium """

        self.driver.quit()

    def make_screenshot(self, file_name):
        if is_screen:
            self.driver.save_screenshot(f'{file_name}.png')

    def clear_page(self):
        """Обновляем страницу и очищаем поля (~0.5 секунды)"""

        self.driver.get(URL_Refresh)

        # self.driver.refresh()
        #
        # sts_field = WebDriverWait(self.driver, 2).until(
        #     EC.presence_of_element_located((By.ID, "checkFinesStsnum")))
        # sts_field.clear()
        #
        # number_field = WebDriverWait(self.driver, 2).until(
        #     EC.presence_of_element_located((By.ID, "checkFinesRegnum"))
        # )
        # number_field.clear()
