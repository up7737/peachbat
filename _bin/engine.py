from time import sleep

# Engine.__init__ dynamic import
from .errors import UrecoverableFailuerError





DELAY = 3
DELAY_MULTIPLIER_ERROR = 3





def p(text, to_terminal=True):
    if to_terminal:
        print(text)


class Tools:
    def persistent_dec(method):
        def persistent_request_wrapper(*args, **kwargs):
            errors = 0
            while True:
                try:
                    sleep(DELAY)
                    response = method(*args, **kwargs)
                    response.raise_for_status()
                    return response
                except Exception as e:
                    errors += 1
                    seconds = errors * DELAY_MULTIPLIER_ERROR
                    if errors > 5: raise UrecoverableFailuerError(e)
                    p('\tErorr {}: {}...\n\tretry in {} seconds'.format(errors, str(e)[:50], seconds))
                    sleep(seconds)
                
        return persistent_request_wrapper


class Engine:
    def __init__(self, library_name):
        self.engine = __import__(library_name)

    @Tools.persistent_dec
    def get(self, url, *, headers, timeout=15):
        response = self.engine.get(url, headers=headers)
        return response

    @Tools.persistent_dec
    def post(self, url, *, headers, data, timeout=15):
        response = self.engine.post(url, headers=headers, data=data)
        return response
