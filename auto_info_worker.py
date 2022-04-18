import json
import signal
import sys
import uuid
from datetime import datetime

import pika
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

import settings
import utils.loggers
from api_lib.sync_api import ApiSync
from api_lib.utils.convert_utils import decode_b64
from api_lib.utils.messages import IncomingMessage
from api_lib.utils.validation_utils import InputParam
from parsers import BotParser
from settings import URL_API, PASS_API, USER_API, SERVICE_NAME_FINES
from utils.loggers import requests_logger


def parse(vin_code: str, method: str = 'all'):
    if vin_code == '':
        return {'error': 'Required parameter is empty'}, False

    vin_code = vin_code.strip()
    # try:
    data_from_parser = parser.parse_data(vin_code, method)
    return data_from_parser['data'], data_from_parser['result'] == 'Success'
    # except (UnexpectedAlertPresentException, RuntimeError):
    #     requests_logger.error('[ERROR] Proxy error')
    #     return {'error': f'Ошибка прокси {WORKER_UUID}'}, False
    # except TimeoutException:
    #     return {'error': f'Превышено время ожидания. Повторите попытку позже {WORKER_UUID}'}, False
    # except Exception as err:
    #     import traceback
    #     requests_logger.error(traceback.format_exc())
    #     return {'error': f'Непредвиденная ошибка парсера {WORKER_UUID} {str(datetime.now())}'}, False


def check_info(message: IncomingMessage):
    data = message.params
    try:
        vin_code = data['vin']
        method_parse = data['method_info']
    except KeyError as ex:
        error = {'error': f'key {str(ex)} not found'}
        requests_logger.info(f" [OR] Wrong request {error=} {WORKER_UUID=}")
        return message.callback_message(error, False)

    try:
        response = parse(vin_code=vin_code, method=method_parse)
        requests_logger.info(f" [Server] response(%s) {WORKER_UUID=}" % (response,))
        send_to_retry = not response[1]
    except Exception as e:
        send_to_retry = True
        requests_logger.error(f'[CI] {e}.')

    if send_to_retry:
        requests_logger.error(f'[CI] Отправка в retryservice')
        json_b64 = decode_b64(message.json())
        api.send_request_api('delay_message', InputParam(name='message_delayed', value=json_b64),
                             requested_service='RETRYSERVICE')
        return

    parser.clear_page()
    requests_logger.info(f" [Server] cleaned page! {WORKER_UUID=}")
    return message.callback_message(response[0], response[1])


if __name__ == '__main__':
    WORKER_UUID = utils.loggers.process_name
    requests_logger.info(f'[INIT] Начало инициализации парсера {WORKER_UUID=}')
    # Запускаем экземпляр селениума один раз
    parser = BotParser(WORKER_UUID)
    requests_logger.info(f'[INIT] Конец инициализации парсера {WORKER_UUID=}')
    api = ApiSync(url=URL_API, pass_api=PASS_API, user_api=USER_API,
                  service_name=settings.SERVICE_NAME_INFO,
                  methods={'check_info': check_info}, is_test=settings.DEBUG)

    api.listen_queue()
