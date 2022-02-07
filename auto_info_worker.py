#!/usr/bin/env python
from datetime import datetime

import pika
import json

from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from utils.custom_exceptions import ProxyError

from utils.validations import validate_sts, ValidationSTSError
from parsers import BotParser
from loggers import requests_logger

requests_logger.info('[INIT] Начало инициализации кролика и парсера')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))

channel = connection.channel()
channel.queue_declare(queue='auto_info_parsed_data')
channel.queue_declare(queue='auto_info_parsing')

parser = BotParser()


def parse(vin_code: str, method: str = 'all'):
    """ Эндпоинт парсинга сайта гибдд """

    if vin_code == '':
        return {'result': 'Fail', 'data': {'error': 'Required parameter is empty'}}

    vin_code = vin_code.strip()
    try:
        data_from_parser = parser.parse_data(vin_code, method)
        return data_from_parser
    except (UnexpectedAlertPresentException, RuntimeError):
        requests_logger.error('[ERROR] Proxy error')
        message_text = 'Парсер ГИБДД\n Прокси не работают'
        # TODO: оповещение в тг
        # send_message(message_text)
        return {'result': 'Fail', 'data': {'error': 'proxy error'}}
    except TimeoutException:
        return {'result': 'Fail', 'data': {'error': 'timeout'}}
    except Exception as err:
        # TODO: Добавлять в логи трейсбек необработанного исключения
        # requests_logger.error(f'Error - {str(err)}')
        # PathL('./gibdd_parser/logs/critical-errors/').mkdir(parents=True, exist_ok=True)
        # error_path = f'gibdd_parser/logs/critical-errors/parser-{str(datetime.now())}.log'
        # with open(error_path, 'w') as log:
        #     traceback.print_exc(file=log)
        return {'result': 'Fail', 'data': {'error': f'Parser error {str(datetime.now())}'}}


def on_request(ch, method, props, body):
    requests_logger.info(" [OR] body(%s)" % (body.decode('utf-8'),))
    data = json.loads(body.decode('utf-8'))
    vin_code, method_parse, uuid = '', '', ''
    try:
        vin_code = data['vin_code']
        method_parse = data['method']
        uuid = data['uuid']
    except KeyError as ex:
        ch.basic_publish(exchange='',
                         routing_key='auto_info_parsed_data',
                         body=str({'result': 'Fail', 'data': {'error': f'key {str(ex)} not found'}}))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    requests_logger.info(" [OR] data(%s)" % (data,))

    response = parse(vin_code=vin_code, method=method_parse)
    response['uuid'] = uuid
    ch.basic_publish(exchange='',
                     routing_key='auto_info_parsed_data',
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

    requests_logger.info(" [Server] response(%s)" % (response,))
    parser.clear_page()
    requests_logger.info(" [Server] cleaned page!")


# channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_message_callback=on_request, queue='auto_info_parsing')

requests_logger.info("[Server] Awaiting RPC requests")
channel.start_consuming()
