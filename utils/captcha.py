"""

Код для решения капчи

"""


from python_rucaptcha import ImageCaptcha
from settings import API_KEY


def rucaptcha_get(path):

    """ Отправляет изображение на рукапчу """
    
    user_answer = ImageCaptcha.ImageCaptcha(rucaptcha_key=API_KEY).captcha_handler(captcha_file=path)

    if not user_answer['error']:

        # решение капчи
        print(user_answer['captchaSolve'])
        return user_answer['captchaSolve']

    elif user_answer['error']:

        # Тело ошибки, если есть
        print(user_answer)
        print(user_answer ['errorBody'])
        raise ValueError
