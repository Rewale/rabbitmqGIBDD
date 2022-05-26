from typing import Tuple, Union

import settings
import utils.loggers
from api_lib.sync_api import ApiSync
from api_lib.utils.convert_utils import decode_b64
from api_lib.utils.messages import IncomingMessage
from api_lib.utils.validation_utils import InputParam
from penalty_parser import BotParserPenalty
from settings import URL_API, PASS_API, USER_API, SERVICE_NAME_FINES
from utils.custom_exceptions import NotFoundSTS
from utils.loggers import requests_logger
from utils.validations import validate_sts, validate_gos_num


def parse(sts, gov_number) -> Tuple[Union[dict, list, str], bool]:
    validate_sts(sts)
    validate_gos_num(gov_number)
    requests_logger.info(f"[INIT] Запрос {gov_number=} {sts=}")
    try:
        data = parser_penalty.parse_data(sts=sts, gov_number=gov_number)
    finally:
        parser_penalty.clear_page()
    requests_logger.info(f" [Server] cleaned page! {WORKER_UUID}")
    if not data:
        return {'error': 'not found'}, False
    return data, True


def fines_parse(message: IncomingMessage):
    """ Обработчик запросов на парсинг """
    requests_logger.info(f" [OR] body(%s) {WORKER_UUID}" % message.params)
    data = message.params

    gov_number = data['gov_number'].upper()
    sts = data['sts']

    try:
        response = parse(gov_number=gov_number, sts=sts)
        requests_logger.info(f" [Server] response(%s) {WORKER_UUID=}" % (response,))
        send_to_retry = not response[1]
    except NotFoundSTS:
        # Отправляем ошибку в конечный сервис
        error_msg = {'error': 'Не найдено ТС с таким сочетанием СТС и ГРЗ'}
        return message.callback_message(error_msg, False)
    except Exception as e:
        send_to_retry = True
        requests_logger.error(f'[FP] {e}.')
    if send_to_retry:
        requests_logger.error(f'[FP] Отправка в retryservice')
        json_b64 = decode_b64(message.json())
        api.send_request_api('delay_message', InputParam(name='message_delayed', value=json_b64),
                             requested_service='RETRYSERVICE')
        return
    requests_logger.info(f" [Server] response(%s) {WORKER_UUID}" % (response,))

    return message.callback_message(response[0], response[1])


if __name__ == '__main__':
    try:
        WORKER_UUID = utils.loggers.process_name
        requests_logger.info(f'[INIT] Начало инициализации парсера {WORKER_UUID}')
        # Запускаем экземпляр селениума один раз
        parser_penalty = BotParserPenalty(WORKER_UUID)
        requests_logger.info(f'[INIT] Конец инициализации парсера {WORKER_UUID}')
        api = ApiSync(url=URL_API, pass_api=PASS_API, user_api=USER_API,
                      service_name=SERVICE_NAME_FINES,
                      heartbeat=120,
                      methods={'penalty': fines_parse}, is_test=settings.DEBUG)

        api.listen_queue()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        del parser_penalty
