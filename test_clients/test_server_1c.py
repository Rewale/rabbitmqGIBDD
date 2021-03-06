""" Эмуляция сервиса """
from datetime import datetime
from time import sleep

import pika
from utils.loggers import requests_logger

requests_logger.info('[INIT] Начало инициализации кролика и парсера')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    virtual_host='/',
    host='192.168.0.216'))

channel = connection.channel()
channel.queue_declare(queue='fines_parsed_data')
channel.queue_declare(queue='fines_parsing')


def on_request(ch, method, props: pika.BasicProperties, body):
    requests_logger.info(" [OR] body(%s)" % (body.decode('utf-8'),))
    response = str(datetime.now()) + f" ID переданный в свойствах :{props.correlation_id}\n{body=}"
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    requests_logger.info(" [Server] response(%s)" % (response,))


# channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_message_callback=on_request, queue='fines_parsing')

requests_logger.info("[Server] Awaiting RPC requests")
channel.start_consuming()
