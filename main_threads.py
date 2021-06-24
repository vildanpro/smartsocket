from threading import Thread
import json
from datetime import datetime
from time import sleep

import requests
from queries import get_new_messages_by_device_id, update_message_if_response_code_200, update_message_with_exception,\
    get_devices


def device_request(message):
    print(message)
    resp_data = {'message_id': message['MESSAGE_ID'], 'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    print(resp_data)
    try:
        with requests.get(message['URI'], timeout=(5, 5)) as resp:
            response_body = json.dumps(resp.json())
            response_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            resp_data.update({'response_code': resp.status_code,
                              'response_date': response_date,
                              'response_body': response_body})
            update_message_if_response_code_200(**resp_data)
            return resp_data
    except Exception as e:
        resp_data.update({'response_code': 408, 'response_body': json.dumps({'Exception': str(e).replace("'", '')})})
        update_message_with_exception(**resp_data)
        return resp_data


class DeviceThread(Thread):
    def __init__(self, device_id, messages):
        super().__init__()
        self.device_id = device_id
        self.messages = messages

    def run(self):
        for message in self.messages:
            device_request(message)


def create_threads():
    devices = get_devices()
    for device in devices:
        device_id = device['DEVICE_ID']
        messages = get_new_messages_by_device_id(device['DEVICE_ID'])
        if messages:
            print(f'Device_id: {device_id}, {len(messages)} new messages')
            new_thread = DeviceThread(device_id, messages)
            new_thread.start()


if __name__ == "__main__":
    while True:
        create_threads()
