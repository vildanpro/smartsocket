from threading import Thread
import json
from datetime import datetime
from time import sleep

import requests
from queries import get_new_messages_by_device_id, update_message_if_response_code_200, update_message_with_exception,\
    get_devices


def device_request(messages):
    for m in messages:
        resp_data = {'message_id': m['MESSAGE_ID'], 'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        print(resp_data)
        try:
            with requests.get(m['URI'], timeout=(5, 5)) as resp:
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
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id

    def run(self):
        while True:
            new_messages = get_new_messages_by_device_id(self.device_id)
            if new_messages:
                print(f'Device_id: {self.device_id}, {len(new_messages)} new messages')
            device_request(new_messages)
            sleep(0)


def create_threads():
    devices = get_devices()
    for device in devices:
        new_thread = DeviceThread(device['DEVICE_ID'])
        new_thread.start()


if __name__ == "__main__":
    create_threads()