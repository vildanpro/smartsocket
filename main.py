import json
from datetime import datetime
import requests
from queries import get_new_messages, update_message_if_response_code_200, update_message_with_exception


def date_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def device_request(m):
    resp_data = {'message_id': m['MESSAGE_ID'], 'request_date': date_now()}
    try:
        with requests.get(m['URI']) as resp:
            response_body = json.dumps(resp.json())
            response_date = date_now()
            resp_data.update({'response_code': resp.status_code,
                              'response_date': response_date,
                              'response_body': response_body})
            update_message_if_response_code_200(**resp_data)
            return resp_data
    except Exception as e:
        resp_data.update({'response_code': 408, 'response_body': json.dumps({'Exception': str(e).replace("'", '')})})
        update_message_with_exception(**resp_data)
        return resp_data


while True:
    for message in get_new_messages():
        print(device_request(message))

