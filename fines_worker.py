import uuid
from datetime import datetime
import pika
import json

from selenium.common.exceptions import TimeoutException
from settings import URL_API, PASS_API, USER_API, SERVICE_NAME
from utils.custom_exceptions import ProxyError
from utils.validations import validate_sts, ValidationSTSError
from penalty_parser import BotParserPenalty
from utils.loggers import requests_logger

from api_lib.sync_api import ApiSync
from api_lib.utils.messages import IncomingMessage


WORKER_UUID = uuid.uuid4()
requests_logger.info(f'[INIT] Начало инициализации кролика и парсера {WORKER_UUID=}')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    virtual_host='/',
    host='192.168.0.216'))

channel = connection.channel()
channel.queue_declare(queue='fines_parsed_data')
channel.queue_declare(queue='fines_parsing')

# Запускаем экземпляр селениума один раз
parser_penalty = BotParserPenalty(WORKER_UUID)


def parse(sts, gov_number):
    # Предварительная валидация, запуск парсинга
    try:
        validate_sts(sts)
        requests_logger.info(f"[INIT] Запрос {gov_number=} {sts=} {WORKER_UUID=}")
        # Выбираем прокси из списка и убираем его
        # available_proxy = proxy_list.pop(choice(range(len(proxy_list))))

        data = parser_penalty.parse_data(sts=sts, gov_number=gov_number)

        # Помещаем обратно в конец
        # proxy_list.append(available_proxy)
        if not data:
            return {'error': 'not found'}, False
        return data
    except ProxyError:
        requests_logger.error('[ERROR] Proxy error')
        # message_text = 'Парсер ГИБДД\n Прокси не работают'
        # send_message(message_text)
        return {'error': 'proxy error'}
    except TimeoutException:
        requests_logger.error('[ERROR] timeout')
        return {'error': 'timeout'}
    except ValidationSTSError as err:
        return {'error': f'{err.text}'}
    except Exception as err:
        requests_logger.error(f'Error - {str(err)}')
        return {'error': f'Parser error {str(datetime.now())}'}


def fines_parse(message: IncomingMessage):
    """ Обработчик запросов на парсинг """
    requests_logger.info(f" [OR] body(%s) {WORKER_UUID=}" % message.params)
    data = message.params
    # Из-за неправильной серилизации 1с
    # data = data['str']
    # Получаем данные для парсинга
    gov_number = data['gov_number']
    sts = data['sts']

    requests_logger.info(f" [OR] data(%s) {WORKER_UUID=}" % (data,))

    response = parse(gov_number=gov_number, sts=sts)

    requests_logger.info(f" [Server] response(%s) {WORKER_UUID=}" % (response,))
    parser_penalty.clear_page()
    requests_logger.info(f" [Server] cleaned page! {WORKER_UUID=}")

    return message.callback_message(response, True)


api = ApiSync(url=URL_API, pass_api=PASS_API, user_api=USER_API, service_name=SERVICE_NAME,
              methods={'fines': fines_parse})
