import uuid
from datetime import datetime
import pika
import json

from selenium.common.exceptions import TimeoutException
from typing import Tuple, Union

import settings
import test_data
import utils.loggers
from api_lib.utils.convert_utils import decode_b64
from api_lib.utils.validation_utils import InputParam
from settings import URL_API, PASS_API, USER_API, SERVICE_NAME_FINES
from utils.custom_exceptions import ProxyError, ServerError, ProcessingError
from utils.validations import validate_sts, ValidationGosNumError, validate_gos_num, ValidationSTSError
from penalty_parser import BotParserPenalty
from utils.loggers import requests_logger

from api_lib.sync_api import ApiSync
from api_lib.utils.messages import IncomingMessage


def parse(sts, gov_number) -> Tuple[Union[dict, list, str], bool]:
    # Предварительная валидация, запуск парсинга
    # TODO: отправка на сервис ретрай
    # try:
    validate_sts(sts)
    validate_gos_num(gov_number)
    requests_logger.info(f"[INIT] Запрос {gov_number=} {sts=}")
    data = parser_penalty.parse_data(sts=sts, gov_number=gov_number)
    if not data:
        return {'error': 'not found'}, False
    return data, True
    # except ProxyError:
    #     requests_logger.error('[ERROR] Proxy error')
    #     return {'error': 'proxy error'}, False
    # except (TimeoutException, ProcessingError):
    #     requests_logger.error('[ERROR] timeout')
    #     return {'error': f'Превышено время ожидания ответа. Повторите попытку позже {WORKER_UUID}'}, False
    # except ServerError:
    #     requests_logger.error(f'[ERROR] Ошибка сервера. Повторите попытку позже')
    #     return {'error': f'Ошибка сервера. Повторите попытку позже {WORKER_UUID}'}, False
    # except (ValidationGosNumError, ValidationSTSError) as err:
    #     return {'error': f'{err.text}'}, False
    # except Exception as err:
    #     requests_logger.error(f'Error - {str(err)}')
    #     return {'error': f'Непредвиденная ошибка парсера {WORKER_UUID} {str(datetime.now())}'}, False


def fines_parse(message: IncomingMessage):
    """ Обработчик запросов на парсинг """
    requests_logger.info(f" [OR] body(%s) {WORKER_UUID}" % message.params)
    data = message.params

    gov_number = data['gov_number'].upper()
    sts = data['sts']

    try:
        response = parse(gov_number=gov_number, sts=sts)
        requests_logger.info(f" [Server] response(%s) {WORKER_UUID=}" % (response,))
        send_to_retry = not response[1]
    except Exception as e:
        send_to_retry = True
        requests_logger.error(f'[FP] {e}.')

    parser_penalty.clear_page()
    if send_to_retry:
        requests_logger.error(f'[FP] Отправка в retryservice')
        json_b64 = decode_b64(message.json())
        api.send_request_api('delay_message', InputParam(name='message_delayed', value=json_b64),
                             requested_service='RETRYSERVICE')
        return
    requests_logger.info(f" [Server] response(%s) {WORKER_UUID}" % (response,))
    requests_logger.info(f" [Server] cleaned page! {WORKER_UUID}")

    return message.callback_message(response[0], response[1])


if __name__ == '__main__':
    WORKER_UUID = utils.loggers.process_name
    requests_logger.info(f'[INIT] Начало инициализации парсера {WORKER_UUID}')
    # Запускаем экземпляр селениума один раз
    parser_penalty = BotParserPenalty(WORKER_UUID)
    requests_logger.info(f'[INIT] Конец инициализации парсера {WORKER_UUID}')
    api = ApiSync(url=URL_API, pass_api=PASS_API, user_api=USER_API,
                  service_name=SERVICE_NAME_FINES,
                  heartbeat=120,
                  methods={'penalty': fines_parse}, is_test=settings.DEBUG)

    api.listen_queue()
