import json
import signal
import sys
import uuid
from datetime import datetime
from time import sleep

import pika
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

import test_data
from api_lib.sync_api import ApiSync
from api_lib.utils.messages import IncomingMessage
from parsers import BotParser
from settings import URL_API, PASS_API, USER_API, SERVICE_NAME
from utils.loggers import requests_logger


def parse(vin_code: str, method: str = 'all'):
    """ Эндпоинт парсинга сайта гибдд """

    if vin_code == '':
        return {'error': 'Required parameter is empty'}, False

    vin_code = vin_code.strip()
    try:
        sleep(5)
        if method == 'registration_history':
            return test_data.test_parse_registation_histoty, True
        elif method == 'restrictions_history':
            return test_data.test_parse_restriction_history, True
        elif method == 'wanted_history':
            return test_data.test_parse_wanted_history , True
        else:
            return {"error": f"Метод {method} не поддерживается"}, False

    except (UnexpectedAlertPresentException, RuntimeError):
        requests_logger.error('[ERROR] Proxy error')
        return {'error': 'proxy error'}, False
    except TimeoutException:
        return {'error': 'timeout'}, False
    except Exception as err:
        import traceback
        requests_logger.error(traceback.format_exc())
        return {'error': f'Parser error {str(datetime.now())}'}, False


def check_info(message: IncomingMessage):
    data = message.params
    try:
        vin_code = data['vin']
        method_parse = data['method_info']
    except KeyError as ex:
        error = {'error': f'key {str(ex)} not found'}
        requests_logger.info(f" [OR] Wrong request {error=} {WORKER_UUID=}")
        return message.callback_message(error, False)

    response = parse(vin_code=vin_code, method=method_parse)
    requests_logger.info(f" [Server] response(%s) {WORKER_UUID=}" % (response,))
    # parser.clear_page()
    requests_logger.info(f" [Server] cleaned page! {WORKER_UUID=}")
    return message.callback_message(response[0], response[1])


if __name__ == '__main__':
    WORKER_UUID = uuid.uuid4()
    requests_logger.info(f'[TEST] Начало инициализации парсера {WORKER_UUID=}')
    # Запускаем экземпляр селениума один раз
    # parser = BotParser(WORKER_UUID)
    api = ApiSync(url=URL_API, pass_api=PASS_API, user_api=USER_API,
                  service_name="GIBDDPROGR",
                  methods={'check_info': check_info})

    api.listen_queue()
