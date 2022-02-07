#!/usr/bin/env python
from datetime import datetime

import pika
import json

from selenium.common.exceptions import TimeoutException
from utils.custom_exceptions import ProxyError

from utils.validations import validate_sts, ValidationSTSError
from penalty_parser import BotParserPenalty
from loggers import requests_logger

requests_logger.info('[INIT] Начало инициализации кролика и парсера')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    virtual_host='/',
    host='192.168.0.216'))

channel = connection.channel()
channel.queue_declare(queue='fines_parsed_data')
channel.queue_declare(queue='fines_parsing')

parser_penalty = BotParserPenalty()


def parse(sts, gov_number):
    try:        
        validate_sts(sts)
        requests_logger.info(f"[INIT] Запрос {gov_number=} {sts=}")
        # Выбираем прокси из списка и убираем его
        # available_proxy = proxy_list.pop(choice(range(len(proxy_list))))

        data = parser_penalty.parse_data(sts=sts, gov_number=gov_number)

        # Помещаем обратно в конец
        # proxy_list.append(available_proxy)
        if not data:
            return {'result': 'Fail', 'data': {'error': 'not found'}}
        return {'result': 'Success', 'data': data}
    except ProxyError:
        requests_logger.error('[ERROR] Proxy error')
        # message_text = 'Парсер ГИБДД\n Прокси не работают'
        # send_message(message_text)
        return {'result': 'Fail', 'data': {'error': 'proxy error'}}
    except TimeoutException:
        requests_logger.error('[ERROR] timeout')
        return {'result': 'Fail', 'data': {'error': 'timeout'}}
    except ValidationSTSError as err:
        return {'result': 'Fail', 'data': {'error': f'{err.text}'}}
    except Exception as err:
        requests_logger.error(f'Error - {str(err)}')
        return {'result': 'Fail', 'data': {'error': f'Parser error {str(datetime.now())}'}}


def on_request(ch, method, props, body):
    requests_logger.info(" [OR] body(%s)" % (body.decode('utf-8'),))
    data = json.loads(body.decode('utf-8'))
    # Из-за неправильной серилизации 1с
    data = data['str']
    gov_number = data['gov_number']
    sts = data['sts']
    uuid = data['uuid']

    requests_logger.info(" [OR] data(%s)" % (data,))

    response = parse(gov_number=gov_number, sts=sts)
    response['uuid'] = uuid
    response['responded_time'] = str(datetime.now())
    ch.basic_publish(exchange='',
                     routing_key='fines_parsed_data',
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

    requests_logger.info(" [Server] response(%s)" % (response,))
    parser_penalty.clear_page()
    requests_logger.info(" [Server] cleaned page!")


# channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_message_callback=on_request, queue='fines_parsing')

requests_logger.info("[Server] Awaiting RPC requests")
channel.start_consuming()
