from pathlib import Path
import socket

import utils.system_utils

URL = 'https://гибдд.рф/check/fines#++'

URL_Refresh = 'https://гибдд.рф/check/fines'
is_screen = False

DOCKER = False

URL_CHECK_AUTO = 'https://xn--90adear.xn--p1ai/check/auto'
# URL_CHECK_AUTO = "https://google.com/"

URL_FINES = 'https://гибдд.рф/check/fines#++'
HOST = '127.0.0.1'
PROXY_API = False
PROXY_PATH = 'proxy_list.json'
PROXY_TYPE = 'all-parsers'

SAVE_FILE_LOG = False

PORT = 8011
DEBUG = True
RELOAD = True
# ?operation=write&extension=" + Строка(РасширениеФайла + "&author=" + Строка(Автор) + "&typedoc=" + Строка(ВидФайла)
# + "&filename=" + Строка(ИмяФайла)
if DEBUG:
    FILES_1C = 'http://192.168.0.7/filesprogr/index.php?operation=write' \
               '&extension=png&author=parserGIBDD&typedoc=2&filename=%s'
else:
    FILES_1C = 'http://192.168.0.7/files/index.php?operation=write' \
               '&extension=png&author=parserGIBDD&typedoc=2&filename=%s'
ITERATIONS = 15

# лимит поиска результата
SEARCH_LIMIT_SEC = 20


ALLOWED_IP_LIST = [
    '0.0.0.0',
    '192.168.0.200',
    '192.168.0.10',
    '192.168.0.219',
    '192.168.0.42',
    '172.22.0.1',
    '172.24.0.1',
    '127.0.0.1',
    '192.168.0.200',
    '192.168.0.10',
    '192.168.0.219',
    '192.168.0.42',
    '172.25.0.1',
    '192.168.0.216',
]


if DOCKER:
    HOST = '0.0.0.0'
    extensions_path = str(Path().parent.absolute()) + '/gibdd_parser/firefox_addons/'
    ALLOWED_IP_LIST.append(str(socket.gethostbyname('cronjobs')))  # автотесты


english_names = {
    'Дата и время происшествия':  'date',
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
