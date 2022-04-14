""" Тестовый клиент, возвращающий 2 штрафа без парсинга """
import uuid
from datetime import datetime
from time import sleep

import pika
import json

from selenium.common.exceptions import TimeoutException
from typing import Tuple, Union

import test_data
from settings import URL_API, PASS_API, USER_API, SERVICE_NAME
from utils.custom_exceptions import ProxyError
from utils.validations import validate_sts, ValidationGosNumError, validate_gos_num, ValidationSTSError
from penalty_parser import BotParserPenalty
from utils.loggers import requests_logger

from api_lib.sync_api import ApiSync
from api_lib.utils.messages import IncomingMessage


def parse(sts, gov_number) -> Tuple[Union[dict, list, str], bool]:
    # Предварительная валидация, запуск парсинга
    try:
        validate_sts(sts)
        validate_gos_num(gov_number)
        requests_logger.info(f"[INIT] Запрос {gov_number=} {sts=} {WORKER_UUID=}")
        requests_logger.info(f"[TEST] 10 секунд ожидания")
        # Эмуляция парсинга
        sleep(10)
        # data = test_data.test_parse_penalty_result
        data = "Штрафов не обнаружено"
        # data = None
        # if not data:
        # return {'error': 'Ошибка парсинга.'}, False
        return data, True
    except ProxyError:
        requests_logger.error('[ERROR] Proxy error')
        # message_text = 'Парсер ГИБДД\n Прокси не работают'
        # send_message(message_text)
        return {'error': 'proxy error'}, False
    except TimeoutException:
        requests_logger.error('[ERROR] timeout')
        return {'error': 'timeout'}, False
    except (ValidationGosNumError, ValidationSTSError) as err:
        return {'error': f'{err.text}'}, False
    except Exception as err:
        requests_logger.error(f'Error - {str(err)}')
        return {'error': f'Parser error {str(datetime.now())}'}, False


def fines_parse(message: IncomingMessage):
    """ Обработчик запросов на парсинг """
    requests_logger.info(f" [OR] body(%s) {WORKER_UUID=}" % message.params)
    data = message.params

    gov_number = data['gov_number'].upper()
    sts = data['sts']
    response = parse(gov_number=gov_number, sts=sts)

    requests_logger.info(f" [Server] response(%s) {WORKER_UUID=}" % (response,))
    requests_logger.info(f" [Server] cleaned page! {WORKER_UUID=}")

    return message.callback_message(response[0], response[1])


if __name__ == '__main__':
    WORKER_UUID = uuid.uuid4()
    requests_logger.info(f'[INIT] Начало инициализации парсера {WORKER_UUID=}')

    # Запускаем экземпляр селениума один раз
    api = ApiSync(url=URL_API, pass_api=PASS_API, user_api=USER_API,
                  service_name=SERVICE_NAME,
                  methods={'penalty': fines_parse})

    api.listen_queue()
