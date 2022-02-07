"""

Модуль хранит настроеные логгеры

"""


from loguru import logger


# логгер запросов
logger.add('gibdd_parser/logs/requests.log',
           format="{time} {level} {message}",
           filter=lambda record: "requests_log" in record["extra"],
           rotation="1 MB",
           compression="tar.gz")

requests_logger = logger.bind(requests_log=True)

# логгер парсера
logger.add('gibdd_parser/logs/parser.log',
           format="[{time} {level} {message}",
           filter=lambda record: "parser_logger" in record["extra"],
           rotation="1 MB",
           compression="tar.gz")

parser_logger = logger.bind(parser_logger=True)
