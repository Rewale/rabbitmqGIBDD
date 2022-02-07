import datetime
from time import sleep

import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(
    virtual_host='/',
    host='192.168.0.216'))

channel = connection.channel()
channel.queue_declare(queue='fines_parsed_data')
# channel.queue_declare(queue='fines_parsing')

minutes = 2

while True:
    sleep(60 * minutes)
    response = "generic_message_2_min"
    channel.basic_publish(exchange='',
                          routing_key='fines_parsed_data',
                          body=str(response))
    print(response)
