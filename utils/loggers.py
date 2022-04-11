"""

Модуль хранит настроенные логгеры

"""
from loguru import logger

# TODO: отдельный файл для каждого воркера
# сохранение логов в файлы (не нужно при вызове супервизором)
# logger.add('/logs/parser.log',
#            format="[{time} {level} {message}",
#            filter=lambda record: "parser_logger" in record["extra"],
#            rotation="1 MB",
#            compression="tar.gz")
# logger.add('/logs/requests.log',
#            format="{time} {level} {message}",
#            filter=lambda record: "requests_log" in record["extra"],
#            rotation="1 MB",
#            compression="tar.gz")

# логгер запросов
requests_logger = logger.bind(requests_log=True)

# логгер парсера
parser_logger = logger.bind(parser_logger=True)
