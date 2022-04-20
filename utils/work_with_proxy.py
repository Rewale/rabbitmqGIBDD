"""
В модуле хранятся функции для работы с прокси
"""

import requests
import json

from loguru import logger

from .telegram import send_message
from utils.custom_exceptions import ProxyError

logger.add('logs/utils.log',
           format="{time} {level} {message}",
           filter=lambda record: "utils" in record["extra"],
           rotation="1 MB",
           compression="tar.gz")
utils_logger = logger.bind(utils=True)


def send_message(message):
    url = 'http://192.168.0.10/wn/hs/apiForSite/sendMessageToSupport'
    print('Отправка сообщений')
    # resp = requests.post(url, auth=('Site', 'glhtopelrflgk5564'), data=message)


def parse_dict(proxy_dict):
    """ Преобразует словарь с прокси в необходимый вид для прокси (список) """

    proxy_list = []

    for proxy in proxy_dict:
        return_string = f"http://{proxy['login']}:{proxy['password']}@{proxy['ip_port']}"
        proxy_list.append(return_string)

    return proxy_list


def read_proxy_json(json_proxy_path, parser_type, use_api):
    """ Считывает proxy с json файла """

    proxy_list = []

    if use_api:
        try:
            proxies = requests.get('http://proxy:8950/proxy').json()
            utils_logger.info(f'Proxies: {proxies}, type: {type(proxies)}')
            if type(proxies) == str:
                raise ProxyError('Файл не найден')
            proxy_dict = proxies[parser_type]
            utils_logger.info(proxy_dict)
            return parse_dict(proxy_dict)
        except KeyError:
            return []

    try:
        with open(json_proxy_path, 'r') as proxy_json:
            proxy_dict = json.load(proxy_json)[parser_type]
            return parse_dict(proxy_dict)
        #      for proxy in proxy_dict:
        #          return_string = f"http://{proxy['login']}:{proxy['password']}@{proxy['ip_port']}"
        #          proxy_list.append(return_string)

        # return proxy_list
    except FileNotFoundError:
        pass
        # send_message('❗️❗️❗️ Отсутсвует файл с прокси ❗️❗️❗️')
        raise ProxyError('Файл не найден')
        # raise RuntimeError('Файл с прокси отсутсвуют')
    except KeyError:
        raise ProxyError('Файл не найден')
        # send_message(❗️❗️❗️ Отсутсвуют прокси для ' + str(parser_type) + ' ❗️❗️❗️)
        # raise RuntimeError('Отсутсвуют прокси для ', parser_type)


def get_proxy_from_api(parser_type):
    try:
        proxies = requests.get('http://proxy:8950/proxy').json()
        utils_logger.info(f'Proxies: {proxies}, type: {type(proxies)}')
        if type(proxies) == str:
            raise ProxyError('Файл не найден')
        proxy_dict = proxies[parser_type]
        utils_logger.info(proxy_dict)
        return parse_dict(proxy_dict)
    except KeyError:
        raise ProxyError(f'Не найден тип прокси: {parser_type}')
