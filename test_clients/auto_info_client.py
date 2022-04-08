import pika
import uuid
import json
import sys

from client_logger import client_request_logger as requests_logger


class ParserRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))

        self.channel = self.connection.channel()
        self.response = None
        self.channel.queue_declare(queue='auto_info_parsed_data')
        result = self.channel.queue_declare(queue='auto_info_parsing')
        self.callback_queue = result.method.queue

        self.channel.basic_consume('auto_info_parsed_data', on_message_callback=self.on_response,
                                   auto_ack=True)

    def on_response(self, ch, method, props, body):
        self.response = body

    def call(self, vin, method):

        n = json.dumps({'vin_code': vin, 'method': method, 'uuid': str(uuid.uuid4())})
        requests_logger.info(f'[ParserClient] {n=}')
        self.response: bytes
        self.channel.basic_publish(exchange='',
                                   routing_key='auto_info_parsing',
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()

        # print(f'{self.response=}')
        return str(self.response.decode('utf-8'))


client = ParserRpcClient()


if __name__ == '__main__':
    response = client.call(sys.argv[1], sys.argv[2])
    requests_logger.info(" [ParserClient] Got %r" % (response,))
