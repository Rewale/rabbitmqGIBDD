import uuid
from datetime import datetime
import pika
import json

from selenium.common.exceptions import TimeoutException
from typing import Tuple, Union

import test_data
from settings import URL_API, PASS_API, USER_API, SERVICE_NAME
from utils.custom_exceptions import ProxyError, ServerError
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
        data = parser_penalty.parse_data(sts=sts, gov_number=gov_number)
        if not data:
            return {'error': 'not found'}, False
        return data, True
    except ProxyError:
        requests_logger.error('[ERROR] Proxy error')
        # message_text = 'Парсер ГИБДД\n Прокси не работают'
        # send_message(message_text)
        return {'error': 'proxy error'}, False
    except TimeoutException:
        requests_logger.error('[ERROR] timeout')
        return {'error': 'Превышено время ожидания ответа. Повторите попытку позже'}, False
    except ServerError:
        requests_logger.error('[ERROR] Ошибка сервера. Повторите попытку позже')
        return {'error': 'Ошибка сервера. Повторите попытку позже'}, False
    except (ValidationGosNumError, ValidationSTSError) as err:
        return {'error': f'{err.text}'}, False
    except Exception as err:
        requests_logger.error(f'Error - {str(err)}')
        return {'error': f'Непредвиденная ошибка парсера {str(datetime.now())}'}, False


def fines_parse(message: IncomingMessage):
    """ Обработчик запросов на парсинг """
    requests_logger.info(f" [OR] body(%s) {WORKER_UUID=}" % message.params)
    data = message.params

    gov_number = data['gov_number'].upper()
    sts = data['sts']
    response = parse(gov_number=gov_number, sts=sts)

    requests_logger.info(f" [Server] response(%s) {WORKER_UUID=}" % (response,))
    parser_penalty.clear_page()
    requests_logger.info(f" [Server] cleaned page! {WORKER_UUID=}")

    return message.callback_message(response[0], response[1])


if __name__ == '__main__':
    WORKER_UUID = uuid.uuid4()
    requests_logger.info(f'[INIT] Начало инициализации парсера {WORKER_UUID=}')
    # Запускаем экземпляр селениума один раз
    parser_penalty = BotParserPenalty(WORKER_UUID)
    api = ApiSync(url=URL_API, pass_api=PASS_API, user_api=USER_API,
                  service_name=SERVICE_NAME,
                  methods={'penalty': fines_parse})

    api.listen_queue()
