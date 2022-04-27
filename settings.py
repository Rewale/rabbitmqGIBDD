import socket
import os
from pathlib import Path

# API rabbit
import utils.loggers

URL_API = 'http://apidev.mezex.lan/getApiStructProgr'
PASS_API = ''
USER_API = ''
SERVICE_NAME_FINES = 'GIBDDPENALTY'
SERVICE_NAME_INFO = 'GIBDD'

URL = 'https://гибдд.рф/check/fines#++'

URL_Refresh = 'https://гибдд.рф/check/fines'
is_screen = False
DOCKER = False

URL_CHECK_AUTO = 'http://xn--90adear.xn--p1ai/check/auto'

URL_FINES = 'https://гибдд.рф/check/fines#++'
HOST = '127.0.0.1'
PROXY_API = False
PROXY_PATH = 'proxy_list.json'
PROXY_TYPE = 'all-parsers'

SAVE_FILE_LOG = False

PORT = 8011
DEBUG = not os.getenv('IS_PROD') == 'True'
utils.loggers.parser_logger.warning(f'[START] {DEBUG=}')
utils.loggers.requests_logger.warning(f'[START] {DEBUG=}')
RELOAD = True
if DEBUG:
    FILES_1C = 'http://192.168.0.7/filesprogr/index.php?operation=write' \
               '&extension=png&author=parserGIBDD&typedoc=2&filename=%s'
else:
    PROXY_API = os.getenv('USE_PROXY') == "True"
    URL_API = os.getenv('URL_API')
    PASS_API = os.getenv('PASS_API')
    USER_API = os.getenv('USER_API')
    FILES_1C = 'http://192.168.0.7/files/index.php?operation=write' \
               '&extension=png&author=parserGIBDD&typedoc=2&filename=%s'
ITERATIONS = 30

# лимит поиска результата
SEARCH_LIMIT_SEC = 20

# скриншоты ошибок
IS_SCREEN = False


english_names = {
    'Дата и время происшествия': 'date',
    'Тип происшествия': 'incedent_type',
    'Регион происшествия': 'region',
    'Место происшествия': 'incedent_place',
    'Марка (модель) ТС': 'venhicle_model',
    'Марка и(или) модель': 'vehicle_brand_or_model',
    'Год выпуска ТС': 'model_product_year',
    'ОПФ собственника': 'opf',
    'Номер ТС/из всего ТС в ДТП': 'tc_number',
    'Год выпуска': 'model_product_year',
    'Идентификационный номер (VIN)': 'vin_code',
    'Номер шасси (рамы)': 'chasis_number',
    'Номер кузова (кабины)': 'body_number',
    'Цвет кузова (кабины)': 'color',
    'Рабочий объем (см³)': 'working_volume',
    'Мощность (кВт/л.с.)': 'power',
    'Тип транспортного средства': 'vehicle_type',
    'Дата постоянного учета в розыске': 'registration_of_wanted_date',
    'Регион инициатора розыска': 'region_of_initiator',
    'Основание': 'reason',
    'Дата наложения ограничения': 'restriction_date',
    'Регион инициатора ограничения': 'restriction_initiator_region',
    'Кем наложено ограничение': 'restricted_by',
    'Вид ограничения': 'restriction_type',
    'Телефон инициатора': 'initiators_phone',
    'Ключ ГИБДД': 'gibdd_key',
    'Номер двигателя': 'engine_number',
    'Описание повреждений': 'damage_description',
}
