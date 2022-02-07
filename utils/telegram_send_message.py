import requests


# TODO Использовать aiohttp
def send_message(message):

    url = 'http://192.168.0.10/wn/hs/apiForSite/sendMessageToSupport'
    message = message.decode('utf-8')
    resp = requests.post(url, auth=('Site', 'glhtopelrflgk5564'), data=message)
    print(resp.status_code)
