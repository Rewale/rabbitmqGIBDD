"""

Модуль хранит настроенные логгеры

"""
from loguru import logger
import os

process_name = os.getenv('SUPERVISOR_PROCESS_NAME')
if process_name:
    if not os.path.isdir(process_name):
        os.mkdir(process_name)
    logger.add(f'logs/{process_name}/{process_name}_parser.log',
               format="[{time} {level} {message}",
               filter=lambda record: "parser_logger" in record["extra"],
               rotation="1 MB",
               compression="tar.gz")
    logger.add(f'logs/{process_name}/{process_name}_requests.log',
               format="{time} {level} {message}",
               filter=lambda record: "requests_log" in record["extra"],
               rotation="1 MB",
               compression="tar.gz")
else:
    process_name = "default_name"

# логгер запросов
requests_logger = logger.bind(requests_log=True)

# логгер парсера
parser_logger = logger.bind(parser_logger=True)
