"""

Модуль хранит настроенные логгеры

"""
from loguru import logger
import os

process_name = os.getenv('SUPERVISOR_PROCESS_NAME')
logger.add(f'logs/{process_name}parser.log',
           format="[{time} {level} {message}",
           filter=lambda record: "parser_logger" in record["extra"],
           rotation="1 MB",
           compression="tar.gz")
logger.add(f'logs/{process_name}requests.log',
           format="{time} {level} {message}",
           filter=lambda record: "requests_log" in record["extra"],
           rotation="1 MB",
           compression="tar.gz")

# логгер запросов
requests_logger = logger.bind(requests_log=True)

# логгер парсера
parser_logger = logger.bind(parser_logger=True)
