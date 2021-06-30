from threading import Thread
import json
from datetime import datetime
import requests
from db import DB
from time import sleep

sleep_seconds = 3
print('\nConnect to DB.', end=' ')
db = DB()


def device_request(message):
    response_data = {'message_id': message['MESSAGE_ID'],
                     'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    print(f"DEVICE_ID: {message['DEVICE_ID']}, MESSAGE_ID: {message['MESSAGE_ID']}, URI: {message['URI']}")
    try:
        with requests.get(message['URI'], timeout=(5, 5)) as resp:
            response_data.update({'response_code': resp.status_code,
                                  'response_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  'response_body': json.dumps(resp.json())})
            db.update_message_if_response_code_200(**response_data)
            return response_data
    except Exception as e:
        response_data.update({'response_code': 408,
                              'response_body': json.dumps({'Exception': str(e).replace("'", '')})})
        db.update_message_with_exception(**response_data)
        return response_data


class DeviceThread(Thread):
    def __init__(self, messages):
        super().__init__(daemon=True)
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
                if device['DEVICE_ID'] == message['DEVICE_ID']:
                    devices_with_messages[device['DEVICE_ID']].append(message)
    thread_list = list()
    for device_id, messages in devices_with_messages.items():
        new_thread = DeviceThread(messages)
        thread_list.append(new_thread)
        thread_list[-1].start()
    for thread in thread_list:
        thread.join()


if __name__ == "__main__":
    print('Start main Loop')
    wait_print = True
    while True:
        new_messages = db.get_new_messages()
        if new_messages:
            devices = db.get_devices()
            if devices:
                print(f'\n\nGet {len(new_messages)} new messages\n')
                print('Create threads')
                create_threads(devices, new_messages)
                print('Threads finished\n\nWait for new messages', end='.')
                wait_print = False
            else:
                print('No devices')
        else:
            if not wait_print:
                print('.', end='')
            else:
                print('\nWait for new messages', end='.')
                wait_print = False

        sleep(sleep_seconds)
