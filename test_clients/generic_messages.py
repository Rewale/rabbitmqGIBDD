import datetime
import uuid
from time import sleep

import pika
from utils.loggers import requests_logger

connection = pika.BlockingConnection(pika.ConnectionParameters(
    virtual_host='/',
    host='192.168.0.216'))

channel = connection.channel()
channel.queue_declare(queue='fines_parsed_data')
# channel.queue_declare(queue='fines_parsing')

minutes = 2
WORKER_UUID = uuid.uuid4()
requests_logger.info(f"Инициализация {WORKER_UUID=}")
while True:
    sleep(2)
    requests_logger.info(f"Пинг {WORKER_UUID=}")
    response = str(datetime.datetime.now())
    channel.basic_publish(exchange='',
                          routing_key='fines_parsed_data',
                          body=str(response))
    print(response)

