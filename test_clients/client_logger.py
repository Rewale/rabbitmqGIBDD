from loguru import logger


# логгер запросов
logger.add('test_clients/clients_request.log',
           format="{time} {level} {message}",
           filter=lambda record: "requests_log" in record["extra"],
           rotation="1 MB",
           compression="tar.gz")

client_request_logger = logger.bind(requests_log=True)
