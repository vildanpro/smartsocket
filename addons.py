import json
import logging
from collections import namedtuple

import requests

from config import device_request_timeout


def make_namedtuple_factory(cursor):
    column_names = [d[0] for d in cursor.description]
    return namedtuple('Row', column_names)


def get_logger():
    logger = logging.getLogger("tasmota_logger")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler("tasmota.log")
    fmt = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger


def device_request(uri):
    logger = get_logger()
    logger.debug(f'Request {uri}')
    print(f'Request {uri}')
    try:
        response = requests.get(uri, timeout=(device_request_timeout, device_request_timeout))
        response_body = json.dumps(response.json())
    except Exception as ee:
        response = None
        response_body = json.dumps({'Exception': str(ee).replace("'", '')})
    if json.loads(response_body).get("Signal"):
        for_print = json.loads(response_body)["Signal"]
    else:
        for_print = 'Timeout'
    logger.debug(f'Response body for request {uri}\n{for_print}')
    print(f'Response {uri}\n{response_body}')
    return {'response_body': response_body, 'response_code': response.status_code if response else 408}

