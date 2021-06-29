from threading import Thread
import json
from datetime import datetime
from time import sleep

import requests
from queries import get_new_messages, update_message_if_response_code_200, update_message_with_exception,\
    get_devices


def device_request(message):
    resp_data = {'message_id': message['MESSAGE_ID'], 'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    print(f"DEVICE_ID: {message['DEVICE_ID']}, MESSAGE_ID: {message['MESSAGE_ID']}, URI: {message['URI']}")
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
        response_body = json.dumps({'Exception': str(e).replace("'", '')})
        resp_data.update({'response_code': 408, 'response_body': response_body})
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


def create_threads(devices, messages):
    devices_with_messages = dict()
    for device in devices:
        devices_with_messages.update({device['DEVICE_ID']: list()})
        if messages:
            for message in messages:
                if device['device_id'] == message['device_id']:
                    devices_with_messages[device['device_id']].append(message)
    for device_id, messages in devices_with_messages.items():
        new_thread = DeviceThread(device_id, messages)
        new_thread.start()


if __name__ == "__main__":
    print('Start')
    wait_print = True
    while True:
        new_messages = get_new_messages()
        if new_messages:
            print('Create threads')
            create_threads(get_devices(), new_messages)
        else:
            if wait_print:
                print('Wait for new messages...')
                wait_print = False

