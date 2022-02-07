#!/usr/bin/env python
import pika
import uuid
import json
import sys
from ..loggers import requests_logger


class ParserRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                virtual_host='test',
                host='192.168.0.216'))

        self.channel = self.connection.channel()
        self.response = None
        self.channel.queue_declare(queue='fines_parsed_data')
        result = self.channel.queue_declare(queue='fines_parsing')
        self.callback_queue = result.method.queue

        self.channel.basic_consume('fines_parsed_data', on_message_callback=self.on_response,
                                   auto_ack=True)

    def on_response(self, ch, method, props, body):
        self.response = body

    def call(self, num, sts):

        n = json.dumps({'gov_number': num, 'sts': sts, 'uuid': str(uuid.uuid4())})
        requests_logger.info(f'[ParserClient] {n=}')
        self.response: bytes
        self.channel.basic_publish(exchange='',
                                   routing_key='fines_parsing',
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()

        # print(f'{self.response=}')
        return str(self.response.decode('utf-8'))


client = ParserRpcClient()


if __name__ == '__main__':
    response = client.call(sys.argv[1], sys.argv[2])
    requests_logger.info(" [ParserClient] Got %r" % (response,))
