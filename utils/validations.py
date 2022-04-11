import re


class ValidationSTSError(Exception):
    def __init__(self, text):
        self.text = text


class ValidationGosNumError(Exception):
    def __init__(self):
        self.text = 'Некорректный гос. номер'


def get_russian_abc():
    """Возвращает массив русских букв в нижнем регистре"""
    a = ord('а')
    return ''.join([chr(i) for i in range(a, a + 32)])


def validate_sts(sts: str) -> bool:
    """Валидация СТС"""

    # Убираем пробелы
    sts = sts.replace(' ', '')
    if len(sts) != 10:
        raise ValidationSTSError('Длина СТС должна быть 10 символов!')
    print(sts)
    # 3 и 4 символ могут быть буквами русского алфавита
    # остальные всегда числа
    if not sts[2].isnumeric() and sts[2].lower() not in get_russian_abc() \
            or not sts[3].isnumeric() and sts[3].lower() not in get_russian_abc():
        raise ValidationSTSError('3 и 4 символ СТС должны быть'
                                 ' числами либо буквами русского алфавита')

    # остальные символы должны быть числами
    part1 = sts[0:2]
    part2 = sts[4:]
    if not part1.isnumeric():
        raise ValidationSTSError('1 и 2 символ должны быть числами')

    if not part2.isnumeric():
        raise ValidationSTSError('Символы с 6 по 10 должны быть числами')

    return True


def validate_gos_num(gos_num: str):
    if len(gos_num) != 9:
        raise ValidationGosNumError()

    pattern = r'^[АВЕКМНОРСТУХ]\d{3}(?<!000)[АВЕКМНОРСТУХ]{2}\d{2,3}$'
    if not re.match(pattern, gos_num):
        raise ValidationGosNumError()
