from api_lib.utils.messages import IncomingMessage
from penalty_parser import BotParserPenalty
from utils.system_utils import get_script_dir, get_firefox_addons_dir


def test_get_addons_dir():
    path = get_firefox_addons_dir()
    assert path == "/home/kolchanovaa/Рабочий стол/parsers/parsers_gibdd_rabbitMQ/utils/firefox_addons"


def test_run_parser():
    """ Нет штрафов """
    sts = '5946436133'
    gov_number = 'Е081СУ159'
    parser_penalty = BotParserPenalty('test_guid')
    data = parser_penalty.parse_data(sts=sts, gov_number=gov_number)
    assert data


def test_run_parser_fines():
    sts = '2335884520'
    gov_number = 'С931РВ123'
    parser_penalty = BotParserPenalty('test_guid')
    try:
        data = parser_penalty.parse_data(sts=sts, gov_number=gov_number)
    except:
        del parser_penalty
        assert False
    print(data)
    del parser_penalty
    assert data == [[{'name': 'Дата и время нарушения:', 'value': '26.08.2018 в 23:30'}, {'name': 'Статья КоАП РФ:',
                                                                                          'value': '12.26 ч.1 - '
                                                                                                   'невыполнение '
                                                                                                   'водителем '
                                                                                                   'законного '
                                                                                                   'требования '
                                                                                                   'сотрудника '
                                                                                                   'полиции о '
                                                                                                   'прохождении '
                                                                                                   'медицинского '
                                                                                                   'освидетельствования на состояние опьянения'},
                     {'name': 'Подразделение ГИБДД:', 'value': 'ОГИБДД и ДПС ОМВД России по г. Анапе'},
                     {'name': 'Постановление:', 'value': '18810423180170013454 от 18.09.2018'},
                     {'name': 'Сумма штрафа:', 'value': '30000 руб.'}],
                    [{'name': 'Дата и время нарушения:', 'value': '20.03.2022 в 17:46'}, {'name': 'Статья КоАП РФ:',
                                                                                          'value': '12.9 ч.2 - '
                                                                                                   'превышение '
                                                                                                   'установленной '
                                                                                                   'скорости движения '
                                                                                                   'транспортного '
                                                                                                   'средства на '
                                                                                                   'величину более '
                                                                                                   '20, но не более '
                                                                                                   '40 км/ч'},
                     {'name': 'Подразделение ГИБДД:',
                      'value': 'ЦАФАПОДД ГИБДД (дислокация г. Краснодар) ГУ МВД России по Краснодарскому краю'},
                     {'name': 'Постановление:', 'value': '18810523220404075459 от 04.04.2022'},
                     {'name': 'Сумма штрафа:', 'value': '500 руб.\nдо 25.04.2022 скидка 250 руб.'}]]


def test_callback_message_list_params():
    data = [[{'name': 'Дата и время нарушения:', 'value': '26.08.2018 в 23:30'}, {'name': 'Статья КоАП РФ:',
                                                                                  'value': '12.26 ч.1 - невыполнение '
                                                                                           'водителем законного '
                                                                                           'требования сотрудника '
                                                                                           'полиции о прохождении '
                                                                                           'медицинского '
                                                                                           'освидетельствования на '
                                                                                           'состояние опьянения'},
             {'name': 'Подразделение ГИБДД:', 'value': 'ОГИБДД и ДПС ОМВД России по г. Анапе'},
             {'name': 'Постановление:', 'value': '18810423180170013454 от 18.09.2018'},
             {'name': 'Сумма штрафа:', 'value': '30000 руб.'}],
            [{'name': 'Дата и время нарушения:', 'value': '20.03.2022 в 17:46'}, {'name': 'Статья КоАП РФ:',
                                                                                  'value': '12.9 ч.2 - превышение '
                                                                                           'установленной скорости '
                                                                                           'движения транспортного '
                                                                                           'средства на величину '
                                                                                           'более 20, но не более 40 '
                                                                                           'км/ч'},
             {'name': 'Подразделение ГИБДД:',
              'value': 'ЦАФАПОДД ГИБДД (дислокация г. Краснодар) ГУ МВД России по Краснодарскому краю'},
             {'name': 'Постановление:', 'value': '18810523220404075459 от 04.04.2022'},
             {'name': 'Сумма штрафа:', 'value': '500 руб.\nдо 25.04.2022 скидка 250 руб.'}]]
    message = IncomingMessage('123', '123', {'test': 'test'}, 'test_method')
    callback = message.callback_message(data, True)
    json_message = callback.json()
    assert json_message
