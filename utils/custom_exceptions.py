class ProxyError(Exception):
    def __init__(self, text):
        self.text = text


class ValidationError(Exception):
    def __init__(self, text):
        self.text = text


class ServerError(Exception):
    pass


class ProcessingError(Exception):
    pass


class NotFoundSTS(Exception):
    pass
