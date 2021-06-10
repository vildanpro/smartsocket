import requests
from datetime import datetime
from collections import namedtuple


def double_quote(data):
    return str(data).replace("'", '"')


def current_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


ResponseTuple = namedtuple('Response', ['request_date', 'response_date', 'response_code', 'response_data'])


def do_device_request(uri, timeout=1):
    print('Выполняется запрос:', uri)
    request_date = current_date()
    response_date = None
    try:
        response = requests.get(uri, timeout=timeout)
        response_date = current_date()
        response_code = response.status_code
        response_data = double_quote(response.json())
    except Exception as e:
        response_code = 408
        response_data = {}
    print('Код ответа', response_code)
    return ResponseTuple(
        request_date=request_date,
        response_date=response_date,
        response_code=response_code,
        response_data=response_data)
