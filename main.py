import json
import logging
from datetime import datetime
from multiprocessing import Process
from time import sleep

import requests

from mongo import MessageModel
from oracle import get_devices, get_new_oracle_messages, oracle_update_message

process_timeout = 3


def get_logger():
    logger = logging.getLogger("tasmota_logger")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler("tasmota.log")
    fmt = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger


def process_func(device_id):
    while True:
        try:
            m = MessageModel.objects.filter(DEVICE_ID=device_id, MESSAGE_STATE_ID=1).first()
            if not m:
                sleep(process_timeout)
                continue
        except Exception as ex:
            print('process_func -> get message', ex)
        else:
            m.REQUEST_DATE  = datetime.now()
            response = None
            log.debug(f'Request {m.URI}')
            try:
                response = requests.get(m.URI, timeout=(30, 30))
                m.RESPONSE_BODY = json.dumps(response.json())
            except Exception as e:
                m.RESPONSE_BODY = json.dumps({'Exception': str(e).replace("'", '')})
            m.MESSAGE_STATE_ID = 21 if response else 24
            m.RESPONSE_CODE = 200 if response else 408
            m.RESPONSE_DATE = datetime.now()
            message_updated = False
            log.debug(f'Response body for request {m.URI}\n{m.RESPONSE_BODY}')
            while not message_updated:
                try:
                    m.save()
                except Exception as ee:
                    print('sqlite message update', ee)
                else:
                    message_updated = True
        sleep(process_timeout)


if __name__ == '__main__':
    log = get_logger()
    print('Start Tasmota script')
    while True:
        try:
            processes_list = [Process(target=process_func, args=(device.DEVICE_ID,)) for device in get_devices()]
            print(f'{len(processes_list)} processes')
        except TypeError as e:
            print('processes_list: no devices')
            continue
        else:
            for process in processes_list:
                process.start()
            print('Processes started...')
        while True:
            try:
                exist = False
                for oracle_message in get_new_oracle_messages():
                    sqlite_messages = MessageModel.objects.filter(DEVICE_ID=oracle_message.DEVICE_ID).all()
                    for sqlite_message in sqlite_messages:
                        if sqlite_message.MESSAGE_ID < oracle_message.MESSAGE_ID:
                            if sqlite_message.RESPONSE_BODY:
                                sqlite_message.delete()
                            else:
                                exist = True
                        elif oracle_message.MESSAGE_ID == sqlite_message.MESSAGE_ID:
                            exist = True
                    if not exist:
                        try:
                            message = MessageModel(
                                MESSAGE_ID=oracle_message.MESSAGE_ID,
                                MESSAGE_TYPE_ID=oracle_message.MESSAGE_TYPE_ID,
                                DEVICE_ID=oracle_message.DEVICE_ID,
                                MESSAGE_STATE_ID=oracle_message.MESSAGE_STATE_ID,
                                URI=oracle_message.URI,
                                RESPONSE_CODE=oracle_message.RESPONSE_CODE,
                                RESPONSE_BODY=oracle_message.RESPONSE_BODY,
                                REQUEST_DATE=oracle_message.REQUEST_DATE,
                                RESPONSE_DATE=oracle_message.RESPONSE_DATE
                            )
                            message.save()

                        except Exception as me:
                            print('save to mongo', me)
                sqlite_done_messages = MessageModel.objects.filter(MESSAGE_STATE_ID__ne=1).all()
                for sqlite_message in sqlite_done_messages:
                    try:
                        oracle_update_message(sqlite_message)
                    except Exception as e:
                        print('main -> oracle_update_message:', e)
                    else:
                        sqlite_message.delete()
            except Exception as e:
                print('message loop', e)
            sleep(1)
