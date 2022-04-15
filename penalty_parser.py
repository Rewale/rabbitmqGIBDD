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
import os
import signal
import sys
import time

# импорты со стронних библиотек
# from selenium import webdriver
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (TimeoutException, )
from selenium.webdriver import ActionChains
# Ожидания
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import settings
import utils.system_utils
from utils.custom_exceptions import ServerError, ProcessingError
from utils.loggers import parser_logger
from utils.parser_fabric import create_driver

URL = 'https://гибдд.рф/check/fines'

SAVE_PATH = utils.system_utils.get_script_dir() + '/Screenshots/%s'
SCREENSHOTS_SAVE_PATH = SAVE_PATH
URL_Refresh = 'https://гибдд.рф/check/fines'
is_screen = settings.IS_SCREEN


class BotParserPenalty:
    """  Бот-парсер вся логика парсера лежит тут """

    def exit_gracefully(self, *args):
        parser_logger.info(f"[EXIT] Kill {self.WORKER_UUID=}")
        self.driver.quit()
        sys.exit(0)

    def __init__(self, WORKER_UUID, option: bool = True, available_proxy=None):

        """
        Инициализация данных, где:

         * gov_number - государственный номер автомобиля.
         * sts - номер свидетельства о регистрации.
        """

        # Очистка памяти при выходе
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self.WORKER_UUID = WORKER_UUID

        self.sts_number = None
        self.gov_number = None
        self.parses_uuid = WORKER_UUID
        self.busy = False

        self.driver = create_driver()
        self.driver.get(URL)
        parser_logger.info(f"[INIT] END {self.parses_uuid=}")

        if is_screen:
            path = SAVE_PATH % self.parses_uuid
            if not os.path.exists(path):
                os.mkdir(path)
            self.screen_path = path
            self.make_screenshot('start.png')
            parser_logger.info(f"[INIT] Screen {path=}")

    def __parse_result(self) -> list:

        """ Парсит результат """
        xpath_not_found = '//*[@id="checkFines"]/p[contains(@class, "check-space check-message")]/p'

        parser_logger.info('[PR] Начало парсинга результата')
        start = time.time()

        # Пытаемся как можно быстрее узнать результат
        while (time.time() - start) < 15:
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
                        # Устанавливаем лимит на ожидания текста в одну секунду
                        # TODO Собственный ЕС
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
        # TODO: Если ошибка сервера - попробовать еще раз
        xpath_processing = '//*[contains(text(), "Выполняется запрос, ждите")]'
        xpath_server_error = '//*[contains(text(), "ошибка сервера")]'
        try:
            self.driver.find_element_by_xpath(xpath_server_error)
            raise ServerError
        except:
            try:
                self.driver.find_element_by_xpath(xpath_processing)
                raise ProcessingError
            except:
                self.make_screenshot('timeout')
                raise TimeoutException

    def __input_values_and_click_button(self) -> None:

        """ Вводит обязательные поля и нажимает на кнопку поиска """

        number = self.gov_number[:6]
        region = self.gov_number[6:]
        parser_logger.info('[IC] Ввод полей')

        try:
            parser_logger.info(f'[IC] Поле гос. номера {self.parses_uuid=}')
            number_field = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.ID, "checkFinesRegnum"))
            )
            number_field.send_keys(number)
        except TimeoutException:
            parser_logger.warning('Бесконечная загрузка')
            load_message = self.driver.find_element_by_xpath('//*[contains(text(), "Идет загрузка")]')
            if is_screen:
                self.make_screenshot('find_errors')
                parser_logger.warning('Сохранен скриншот')
            if load_message:
                # Перезагружаем страницу и пробуем еще раз
                self.clear_page()
                parser_logger.info(f'[IC] Повторный ввод поля гос. номера {self.parses_uuid=}')
                number_field = WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((By.ID, "checkFinesRegnum"))
                )
                number_field.send_keys(number)

        parser_logger.info(f'[IC] Поле региона {self.parses_uuid=}')
        # region_field = self.driver.find_element_by_id('checkFinesRegreg')
        region_field = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.ID, "checkFinesRegreg"))
        )
        region_field.send_keys(region)

        parser_logger.info(f'[IC] Поле свидетельства о регистрации {self.parses_uuid=}')
        # sts_field = self.driver.find_element_by_id('checkFinesStsnum')
        sts_field = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.ID, "checkFinesStsnum")))
        sts_field.send_keys(self.sts_number)

        # sleep(2)
        parser_logger.info(f'[IC] Нажатие на кнопку поиска {self.parses_uuid=}')
        # search_button = self.driver. \
        #     find_element_by_xpath('//*[contains(text(), "запросить проверку")]')

        self.make_screenshot(f'button{datetime.datetime.now()}.png')
        search_button = WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "запросить проверку")]')))

        parser_logger.info(f'[IC] Найдена кнопка поиска {str(search_button)}')
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
            self.driver.save_screenshot(self.screen_path + f'/{file_name}.png')

    def clear_page(self):
        # """ Очищаем форму с помощью кнопки, если ее нет перезагружаем страницу"""
        # try:
        #     clear_form = WebDriverWait(self.driver, 0.2).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "очистить форму")]')))
        #     clear_form.click()
        #     parser_logger.info("[CP] Очистка формы")
        # except TimeoutException:
        #     self.driver.get(URL_Refresh)
        #     parser_logger.warning("[CP] Обновление формы. Кнопка очистки не найдена!")
        self.driver.get(URL_Refresh)
