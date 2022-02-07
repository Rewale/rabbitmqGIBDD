# import datetime
# from time import sleep
#
# import pika
#
#
# connection = pika.BlockingConnection(pika.ConnectionParameters(
#     virtual_host='/',
#     host='192.168.0.216'))
#
# channel = connection.channel()
# channel.queue_declare(queue='fines_parsed_data')
# # channel.queue_declare(queue='fines_parsing')
#
#
# channel.basic_publish(exchange='',
#                       routing_key='fines_parsed_data',
#                       body=response)
#
