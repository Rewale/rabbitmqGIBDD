class ProxyError(Exception):
    def __init__(self, text):
        self.text = text


class ValidationError(Exception):
    def __init__(self, text):
        self.text = text
