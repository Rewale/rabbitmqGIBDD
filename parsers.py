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

# иморт с локальных модулей
import utils
from settings import URL as URL, english_names, ITERATIONS, SEARCH_LIMIT_SEC, FILES_1C
from settings import PROXY_PATH, PROXY_TYPE, PROXY_API
from utils.loggers import parser_logger
from utils.system_utils import get_script_dir
from utils.work_with_proxy import read_proxy_json

# импорт с локальных модулей
from settings import URL_CHECK_AUTO as URL, english_names, ITERATIONS, SEARCH_LIMIT_SEC
from settings import PROXY_PATH, PROXY_TYPE, PROXY_API
from utils.loggers import parser_logger
from utils.work_with_proxy import read_proxy_json

IMAGES_BASE_URL = 'http://192.168.0.200:8010/gibdd/api/v1/images/'
BAD_VIN_LIST = ['Сначала нужно ввести идентификационный номер транспортного средства (VIN)',
                'Введите VIN, номер кузова или номер шасси.']

is_screen = False
SAVE_PATH = get_script_dir()+'/%s'
SCREENSHOTS_SAVE_PATH = SAVE_PATH+'/screenshots'


class BotParser:
    """  Бот-парсер вся логика парсера лежит тут """

    def exit_gracefully(self, *args):
        parser_logger.info(f"[EXIT] Kill {self.WORKER_UUID=}")
        self.driver.quit()
        sys.exit(0)

    def __init__(self, WORKER_UUID):
        # Очистка памяти при выходе
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self.WORKER_UUID = WORKER_UUID
        self.code = None
        self.parser_method = None

        # путь для расширений Firefox
        extensions_path = '/home/kolchanovaa/Рабочий стол/parsers/' \
                          'parsers_gibdd_rabbitMQ/utils/firefox_addons/ublock_origin.xpi'

        # юзер агент и прокси
        user_agent = UserAgent().firefox
        # self.proxy_list = read_proxy_json(PROXY_PATH, PROXY_TYPE, PROXY_API)
        # self.proxy = choice(self.proxy_list)
        # test_proxy(self.proxy, self.URL)

        options = webdriver.FirefoxOptions()
        # options.add_argument("start-maximized")
        # options.add_argument("disable-infobars")
        # options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.headless = True

        profile = webdriver.FirefoxProfile()
        profile.add_extension(extension=extensions_path)
        # self.driver.install_addon(f'{extensions_path}ublock_origin.xpi',)
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
        self.driver = webdriver.Firefox(options=options, seleniumwire_options=sw_options, firefox_profile=profile)
        # self.driver = webdriver.Firefox()#seleniumwire_options=options)
        self.driver.set_page_load_timeout(40)

        self.driver.install_addon(f'{extensions_path}', )
        self.driver.set_window_size(1200, 1200)
        self.driver.get(URL)

        if is_screen:
            path = SAVE_PATH % self.WORKER_UUID
            os.mkdir(path)
            self.screen_path = SCREENSHOTS_SAVE_PATH % self.WORKER_UUID
            os.mkdir(self.screen_path)
            self.make_screenshot('start.png')
            parser_logger.info(f"[INIT] Screen {path=}")
    #        self.driver.get('http://2ip.ru')

    def _remove_interfering_windows(self, numeric=True):

        """ Убирает окно ввода цифр """

        # закрывает окно с вводом цифр
        if numeric:
            try:
                close_span = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.ID, "captchaSubmit"))
                )
                close_span.click()
                parser_logger.info("[NUMBER-FIELD]Кнопка ввода цифр")
            except Exception:
                pass

    def make_screenshot(self, file_name):
        if is_screen:
            self.driver.save_screenshot(self.screen_path+f'/{file_name}.png')

    def _send_field_orig(self):

        """ Отправляет код в input_field """

        parser_logger.info("Отправка кода в input_field ")

        try:
            input_field = self.driver.find_element_by_id("checkAutoVIN")
            input_field.send_keys(self.code)
            parser_logger.info("Ввод VIN кода: %s" % self.code)
            return True
        except NoSuchElementException:
            parser_logger.info("Страница не прогрузилась, повторная отправка VIN кода")
            sleep(10)
            try:
                load_message = self.driver.find_element_by_xpath('//*[contains(text(), "Идет загрузка")]')
                if load_message:
                    parser_logger.warning('Бесконечная загрузка')
                    raise TimeoutException
                sleep(0.5)
            except NoSuchElementException:
                pass
            return False
            # self._send_field()

    def _send_field_waits(self):

        """ Отправляет код в input_field """
        parser_logger.info("Отправка кода в input_field ")
        try:
            input_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'checkAutoVIN'))
            )
            input_field.send_keys(self.code)
            parser_logger.info("Ввод VIN кода: %s" % self.code)
            return True
        except TimeoutException:
            parser_logger.info("Страница не прогрузилась, повторная отправка VIN кода")
            return False

    def _send_field(self):
        """Интерфейс для переключения версий методов ввода"""
        return self._send_field_waits()

    def _save_road_accident_image_api(self, data_block):

        """ Сохраняет изображение """

        parser_logger.info("[ACCIDENT-I] Получение изображений ДТП")
        save_path = str(uuid.uuid4()) + '.jpg'
        parser_logger.info("[ACCIDENT-I] Путь сохранения: ./dtp_images/{save_path}")
        image_element = data_block.find_element_by_tag_name('tbody')
        image_element.screenshot('./gibdd_parser/dtp_images/' + save_path)
        return IMAGES_BASE_URL + save_path

    def _save_road_accident_image_1c(self, data_block):

        """ Сохраняет изображение """
        import requests
        import base64

        parser_logger.info("[ACCIDENT-I] Получение изображений ДТП")
        filename = str(datetime.datetime.now()).replace(' ','') + '.jpg'
        url = FILES_1C % (filename, )
        parser_logger.info(f"[ACCIDENT-I] Отправка изображения в сервис {url}")
        image_element = data_block.find_element_by_tag_name('tbody')
        try:
            screenshot_as_bytes = image_element.screenshot_as_png
            screenshot_as_base64 = base64.b64encode(screenshot_as_bytes)
            image_uuid = requests.post(url, data=screenshot_as_base64).text
        except Exception as e:
            parser_logger.info(f"[ACCIDENT-I] Ошибка отправки изображения: {str(e)}")
            return "error"

        parser_logger.info(f"[ACCIDENT-I] UUID изображения на сервисе {image_uuid}")
        return image_uuid

    def _save_road_accident_image(self, data_block):

        """ Сохраняет изображение """

        parser_logger.info("[ACCIDENT-I] Получение изображений ДТП")
        save_path = str(uuid.uuid4()) + '.jpg'
        parser_logger.info("[ACCIDENT-I] Путь сохранения: ./dtp_images/{save_path}")
        image_element = data_block.find_element_by_tag_name('tbody')
        image_element.screenshot('./gibdd_parser/dtp_images/' + save_path)
        return IMAGES_BASE_URL + save_path

    def _change_dtp_output(self, result):

        """ Изменяет формат выходных данных о ДТП """

        return_dict = []
        li_parent_elements = result.find_elements_by_xpath('./ul/li')
        for iteration, item in enumerate(li_parent_elements):
            local_dict = {}
            local_dict['accident_id'] = item.find_element_by_class_name('ul-title'). \
                text.split('№')[1].strip()
            li_data_elements = item.find_elements_by_xpath('./ul/li')
            for li_el in li_data_elements:
                key = li_el.find_element_by_class_name('caption').text.strip()[:-1]
                value = li_el.find_element_by_class_name('field').text.strip()
                try:
                    english_key = english_names[key]
                    local_dict[english_key] = value
                except KeyError:
                    parser_logger.error(f'Отсутсвует английское имя: {key}')
                    local_dict[key] = value
            damage_desc_li = item.find_elements_by_xpath('./ul/ul/li')
            if damage_desc_li:
                local_dict['damage_desc'] = [li.text for li in damage_desc_li[1:]]
            else:
                local_dict['damage_desc'] = []

            local_dict['images'] = self._save_road_accident_image_1c(item)
            return_dict.append(local_dict)

        full_dict = {'dtp_list': return_dict}

        return full_dict

    def _change_data_output_format(self, data, is_string=True):

        """ Изменяет формат выходных данных периода регистрации """

        # return_data = []
        return_dict = {}
        iteration = 0
        # periods = {'periods_of_vehicle_ownership': []}
        periods = []
        period = False
        if is_string:
            data = data.split('\n')
        while iteration < len(data):
            if data[iteration] == "Периоды владения транспортным средством" or period:
                period = True
                iteration_data = data[iteration].split(' ')
                parser_logger.info(f"[REGISTRATION-DATA]: {iteration_data}")
                if data[iteration].split(' ')[0] == 'c':
                    periods.append(data[iteration])
                iteration += 1
            if not period:
                # return_data.append(data[iteration] + data[iteration+1])
                name = data[iteration].split(':')[0]
                try:
                    return_dict[english_names[name]] = data[iteration + 1]
                except KeyError:
                    parser_logger.error(f'Отсутсвует английское имя: {name}')
                    return_dict[name] = data[iteration + 1]
                iteration += 2

        parser_logger.info(f'[DATA]: {return_dict}')
        return_dict['periods_of_vehicle_ownership'] = periods
        return_dict['last_operation'] = data[-1]

        return return_dict

    def _get_template_data(self, result, restriction=False):

        """ Шаблон для получения данных истории ограничений и розыске """

        # list_ = result.find_elements_by_tag_name('p')
        list_ = result.find_elements_by_class_name('ul-title')
        # all_local_li = result.find_elements_by_tag_name('li')
        # return_data = [li.text.strip() for li in all_local_li]

        all_li = [tag.find_element_by_xpath('..') for tag in list_]
        return_data = []
        for li in all_li:
            return_dict = {}
            all_local_li = li.find_elements_by_tag_name('li')
            for num in range(0, len(all_local_li)):
                li_text = all_local_li[num].text
                text_split = li_text.split(':')
                if li_text:
                    name = text_split[0].strip()
                    value = text_split[1].strip()
                    try:
                        if restriction and name == 'Основание':
                            # inner_data = li_text.split(':')
                            # reason_dict = {}
                            # for iteration in range(1, len(text_split)-1, 2):
                            #     reason_dict[text_split[iteration]] = text_split[iteration+1]
                            # return_dict[english_names[name]] = reason_dict
                            return_dict[english_names[name]] = li_text.split('\n')[1]
                        else:
                            return_dict[english_names[name]] = value
                    except KeyError:
                        return_dict[name] = value
                        parser_logger.error(f'Отсутсвует английское имя: {name}')
            return_data.append(return_dict)
            parser_logger.info(f'Данные: {return_dict}')
        return return_data

    @staticmethod
    def _check_vin_errors(parent_div):
        """Проверка ошибок вин номера на сайте"""
        try:
            alert_div = parent_div.find_element_by_class_name('alertDiv')
            if alert_div.text in BAD_VIN_LIST:
                return 'Указан некорректный идентификатор транспортного средства (VIN).'
        except NoSuchElementException:
            pass
        message = parent_div.find_element_by_class_name('check-message').text
        if message == 'Указан некорректный идентификатор транспортного средства (VIN).':
            return message
        if message == 'По указанному VIN не найдена информация о регистрации транспортного средства.':
            return message

    def _get_registration_history(self):

        """ Получает историю регистрации """

        parser_logger.info('[REGISTRATION]Старт получения данных истории регистрации')
        button_exist, iteration = True, 0
        parent_div = self.driver.find_element_by_id('checkAutoHistory')

        while button_exist:
            try:
                parser_logger.info("[REGISTRATION-BUTTON]Кнопка нажата")
                # self._remove_interfering_windows()
                try:
                    alert_div = parent_div.find_element_by_class_name('alertDiv')
                    if alert_div.text in BAD_VIN_LIST:
                        return 'Указан некорректный идентификатор транспортного средства (VIN).'
                except NoSuchElementException:
                    pass
                message = parent_div.find_element_by_class_name('check-message').text
                if message == 'Указан некорректный идентификатор транспортного средства (VIN).':
                    return message
                if message == 'По указанному VIN не найдена информация о регистрации транспортного средства.':
                    return message

                sleep(0.5)
                tracing_button = self.driver. \
                    find_element_by_link_text('запросить сведения о периодах регистрации')
                tracing_button.click()

            except NoSuchElementException:

                try:
                    # если не найдет - поднимется NoSuchElementException
                    self.driver.find_element_by_id('registerStatement')
                    parser_logger.info('[REGISTRATION-DATA] Данные прогрузились')

                    sleep(1)
                    unparsed_data = self.driver.find_element_by_class_name('checkResult').text

                    button_exist = False
                    return_data = self._change_data_output_format(unparsed_data)

                    return return_data

                except NoSuchElementException:
                    self.make_screenshot('registration_not_found.png')
                    sleep(0.5)
                    iteration += 1
                    if iteration == ITERATIONS:
                        raise RuntimeError

            except ElementClickInterceptedException:
                message = 'Указан некорректный идентификатор транспортного средства (VIN).'
                return message

    def _get_registration_history_webdriver_wait(self):

        """История регистрации с использованием явных ожиданий"""

        parser_logger.info('[REGISTRATION]Старт получения данных истории регистрации')
        parent_div = self.driver.find_element_by_id('checkAutoHistory')

        # self._remove_interfering_windows()
        try:
            alert_div = parent_div.find_element_by_class_name('alertDiv')
            if alert_div.text in BAD_VIN_LIST:
                return 'Указан некорректный идентификатор транспортного средства (VIN).'
        except NoSuchElementException:
            pass
        message = parent_div.find_element_by_class_name('check-message').text
        if message == 'Указан некорректный идентификатор транспортного средства (VIN).':
            return message
        if message == 'По указанному VIN не найдена информация о регистрации транспортного средства.':
            return message

        # sleep(0.5)
        # tracing_button = self.driver. \
        #     find_element_by_link_text('запросить сведения о периодах регистрации')
        tracing_button = WebDriverWait(self.driver, 0.5).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, 'запросить сведения о периодах регистрации')
            )
        )
        parser_logger.info("[REGISTRATION-BUTTON] Нажата кнопка поиска")

        tracing_button.click()
        try:
            # если не найдет - поднимется NoSuchElementException
            # self.driver.find_element_by_id('registerStatement')
            reg = WebDriverWait(self.driver, 2.5).until(
                EC.presence_of_element_located(
                    (By.ID, 'registerStatement')
                )
            )
            parser_logger.info('[REGISTRATION-DATA] Данные прогрузились')

            # sleep(1)
            # unparsed_data = self.driver.find_element_by_class_name('checkResult').text
            result_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'checkResult')
                )
            )
            parser_logger.info("[REGISTRATION-PARSING] Найден блок результатов")
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="checkAutoHistory"]/div/ul/li'))
            )
            unparsed_data = result_element.text
            parser_logger.info(f"[REGISTRATION-PARSING] Найдены результаты {unparsed_data=}")
            button_exist = False
            return_data = self._change_data_output_format(unparsed_data)
        except TimeoutException as e:
            self.make_screenshot('timeout_history.png')
            raise e

        return return_data

    def _get_road_accident_history(self):

        """ Получает историю ДТП """

        parser_logger.info("[ACCIDENT]Старт получения данных о ДТП")

        parent_div = self.driver.find_element_by_id('checkAutoAiusdtp')
        button_exist, iteration = True, 0

        while button_exist:

            try:
                try:
                    alert_div = parent_div.find_element_by_class_name('alertDiv')
                    if alert_div.text in BAD_VIN_LIST:
                        return 'Указан некорректный идентификатор транспортного средства (VIN).'
                except NoSuchElementException:
                    pass
                tracing_button = self.driver. \
                    find_element_by_link_text('запросить сведения о ДТП')

                tracing_button.click()
                parser_logger.info("[ACCIDENT-BUTTON]Кнопка нажата")
                self._remove_interfering_windows()

            except NoSuchElementException:
                try:
                    result = parent_div.find_element_by_class_name('checkResult')
                    result_text = result.text.strip()
                    # parser_logger.info(f'[ACCIDENT-DATA] Текст: {result_text}')
                    if result_text == '':
                        parser_logger.info("[ACCIDENT-DATA] Поднятие ошибки NoSuchElementException")
                        try:
                            result_p = parent_div.find_elements_by_tag_name('p')
                            check_result = result_p[1].text.strip()
                            if check_result == 'В результате обработки запроса к АИУС ГИБДД ' + \
                                    'записи о дорожно-транспортных происшествиях не найдены.':
                                parser_logger.info(f'[ACCIDENT-DATA]: Результат -  {check_result}')
                                return check_result
                        except IndexError:
                            pass
                        raise NoSuchElementException

                    return_data = self._change_dtp_output(result)
                    self.make_screenshot(f'dtp_found_at_iter_{iteration}.png')
                    button_exist = False
                    return return_data

                except NoSuchElementException:
                    sleep(0.5)
                    iteration += 1
                    parser_logger.info(f"[ACCIDENT-DATA] Элемент не найден, итерация: {iteration}")
                    if iteration == ITERATIONS:
                        raise RuntimeError

    def _get_road_accident_history_webdriver_wait(self):

        """История регистрации с использованием явных ожиданий"""

        parser_logger.info('[ACCIDENT]Старт получения данных истории регистрации')
        parent_div = self.driver.find_element_by_id('checkAutoAiusdtp')

        self._remove_interfering_windows()

        tracing_button = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'запросить сведения о ДТП'))
        )

        tracing_button.click()
        parser_logger.info("[ACCIDENT-BUTTON]Кнопка нажата")
        # self.driver.find_element_by_id('registerStatement')

        errors = BotParser._check_vin_errors(parent_div)
        if errors:
            return errors

        parser_logger.info("[ACCIDENT-BUTTON]Начало парсинга")
        start_time = time.time()
        unparsed_data = ''
        while start_time - time.time() < SEARCH_LIMIT_SEC:
            unparsed_data = WebDriverWait(self.driver, 1.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'checkResult'))
            ).text
            if unparsed_data:
                break
            else:
                try:
                    result_p = parent_div.find_elements_by_tag_name('p')
                    check_result = result_p[1].text.strip()
                    if check_result == 'В результате обработки запроса к АИУС ГИБДД ' + \
                            'записи о дорожно-транспортных происшествиях не найдены.':
                        parser_logger.info(f'[ACCIDENT-DATA]: Результат -  {check_result}')
                        return check_result
                except IndexError:
                    pass
        parser_logger.info(f'[ACCIDENT-DATA] Данные прогрузились {unparsed_data=}')
        return_data = self._change_dtp_output(unparsed_data)

        return return_data

    def _get_tracing_history(self):

        """ Получает историю розыска """

        parser_logger.info("[TRACING]Старт получения истории розыска ")
        parent_div = self.driver.find_element_by_id("checkAutoWanted")

        button_exist, iteration = True, 0

        while button_exist:
            try:
                try:
                    alert_div = parent_div.find_element_by_class_name('alertDiv')
                    if alert_div.text in BAD_VIN_LIST:
                        return 'Указан некорректный идентификатор транспортного средства (VIN).'
                except NoSuchElementException:
                    pass
                tracing_button = self.driver. \
                    find_element_by_link_text('запросить сведения о розыске')
                tracing_button.click()
                parser_logger.info("[TRACING-BUTTON]Кнопка нажата")
                self._remove_interfering_windows()
            except NoSuchElementException:
                try:
                    result = parent_div.find_element_by_class_name('checkResult')
                    result_text = result.text.strip()
                    # parser_logger.info(f'[TRACING-DATA] Текст: {result_text}')
                    if result_text == '':
                        parser_logger.info("[TRACING-DATA] Поднятие ошибки NoSuchElementException")
                        try:
                            result_p = parent_div.find_elements_by_tag_name('p')
                            check_result = result_p[1].text.strip()
                            if check_result == 'По указанному VIN (номер кузова или шасси) ' + \
                                    'не найдена информация о розыске транспортного средства.':
                                parser_logger.info(f'[TRACING-DATA]: Результат -  {check_result}')
                                return check_result
                        except IndexError:
                            pass
                        raise NoSuchElementException

                    return_data = self._get_template_data(result)
                    button_exist = False
                    return return_data

                except NoSuchElementException:
                    sleep(0.5)
                    iteration += 1
                    parser_logger.info(f"[TRACING-DATA] Элемент не найден, итерация: {iteration}")
                    if iteration == ITERATIONS:
                        raise RuntimeError

    def _get_restrictions_history(self):

        """ Получает историю ограничений """

        # скролит вниз
        self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        parser_logger.info("[RESTRICTIONS]Старт получения истории ограничений ")
        parent_div = self.driver.find_element_by_id("checkAutoRestricted")

        button_exist, iteration = True, 0

        while button_exist:
            try:
                try:
                    alert_div = parent_div.find_element_by_class_name('alertDiv')
                    if alert_div.text in BAD_VIN_LIST:
                        return 'Указан некорректный идентификатор транспортного средства (VIN).'
                except NoSuchElementException:
                    pass
                tracing_button = self.driver. \
                    find_element_by_link_text('запросить сведения об ограничениях')
                tracing_button.click()
                parser_logger.info("[RESTRICTIONS-BUTTON]Кнопка нажата")

                self._remove_interfering_windows()
            except NoSuchElementException:
                try:
                    result = parent_div.find_element_by_class_name('checkResult')
                    result_text = result.text.strip()
                    # parser_logger.info(f'[RESTRICTIONS-DATA] Текст: {result_text}')
                    if result_text == '':
                        parser_logger.info("[RESTRICTIONS-DATA]" + \
                                           "Поднятие ошибки NoSuchElementException")
                        try:
                            result_p = parent_div.find_elements_by_tag_name('p')
                            check_result = result_p[1].text.strip()
                            if check_result == 'По указанному VIN (номер кузова или шасси) ' + \
                                    'не найдена информация о наложении ограничений на регистрационные ' + \
                                    'действия с транспортным средством.':
                                parser_logger.info(f'[RESTRICTIONS-DATA]: Результат-{check_result}')
                                return check_result
                        except IndexError:
                            pass
                        raise NoSuchElementException

                    # all_local_li = result.find_elements_by_tag_name('li')
                    # return_data = [li.text for li in all_local_li]
                    # parser_logger.info(f'[RESTRICTIONS-DATA] Данные найдены {return_data}')
                    button_exist = False

                    return_data = self._get_template_data(result, restriction=True)
                    return return_data

                except NoSuchElementException:
                    sleep(0.5)
                    iteration += 1
                    parser_logger.info("[RESTRICTIONS-DATA] " + \
                                       f"Элемент не найден, итерация: {iteration}")
                    if iteration == ITERATIONS:
                        raise RuntimeError

    def parse_data(self, code, method):

        """ Основная функция парсинга данных """
        self.code = code
        self.parser_method = method.strip().split(',')

        iteration_send = 0
        while True:
            if self._send_field():
                break
            iteration_send += 1
            sleep(0.5)
            if iteration_send == ITERATIONS:
                raise RuntimeError

        return_data = {'result': 'Success', 'data': {}}
        try:
            if 'registration_history' in self.parser_method or 'all' in self.parser_method:
                data = self._get_registration_history_webdriver_wait()
                if data == 'Указан некорректный идентификатор транспортного средства (VIN).':
                    return {'result': 'Fail',
                            'data': {'error': 'Invalid vehicle identifier (vin)'}}
                if data == 'По указанному VIN не найдена информация о регистрации транспортного средства.':
                    return {'result': 'Fail',
                            'data': {'error': 'Not find vehicle identifier (vin)'}}
                else:
                    return_data['data']['registration_history'] = data
            if 'road_accident_history' in self.parser_method or 'all' in self.parser_method:
                data2 = self._get_road_accident_history()
                if data2 == 'Указан некорректный идентификатор транспортного средства (VIN).':
                    return {'result': 'Fail',
                            'data': {'error': 'Invalid vehicle identifier (vin)'}}
                if data2 == 'По указанному VIN не найдена информация о регистрации транспортного средства.':
                    return {'result': 'Fail',
                            'data': {'error': 'Not find vehicle identifier (vin)'}}
                else:
                    return_data['data']['road_accident_history'] = data2
            if 'wanted_history' in self.parser_method or 'all' in self.parser_method:
                data3 = self._get_tracing_history()
                if data3 == 'Указан некорректный идентификатор транспортного средства (VIN).':
                    return {'result': 'Fail',
                            'data': {'error': 'Invalid vehicle identifier (vin)'}}
                if data3 == 'По указанному VIN не найдена информация о регистрации транспортного средства.':
                    return {'result': 'Fail',
                            'data': {'error': 'Not find vehicle identifier (vin)'}}
                else:
                    return_data['data']['wanted_history'] = data3

            if 'restrictions_history' in self.parser_method or 'all' in self.parser_method:
                data4 = self._get_restrictions_history()
                if data4 == 'Указан некорректный идентификатор транспортного средства (VIN).':
                    return {'result': 'Fail',
                            'data': {'error': 'Invalid vehicle identifier (vin)'}}
                if data4 == 'По указанному VIN не найдена информация о регистрации транспортного средства.':
                    return {'result': 'Fail',
                            'data': {'error': 'Not find vehicle identifier (vin)'}}
                else:
                    return_data['data']['restrictions_history'] = data4

        except RuntimeError:
            return {'result': 'Fail', 'data': {'error': 'Ко'}}

        return return_data

    def __del__(self):

        """ При удалении экземпляра класса закрывает соединение с selenium """
        parser_logger.info("[DEL] Удаление экземпляра воркера")
        self.driver.quit()

    def clear_page(self):
        """Обновляем страницу и очищаем поля (~0.5 секунды)"""

        self.driver.get(URL)
