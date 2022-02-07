import requests


def send_message(message):

    url = 'http://192.168.0.10/wn/hs/apiForSite/sendMessageToSupport'
    resp = requests.post(url, auth=('Site', 'glhtopelrflgk5564'), data=message)
    print(resp.status_code)
