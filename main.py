from multiprocessing import Process
from time import sleep
from datetime import datetime
from addons import device_request
from mongo_db import mongo_get_done_messages, mongo_insert_message, mongo_delete_message, mongo_get_messages, \
    mongo_get_message
from oracle_db import oracle_get_new_messages, oracle_update_message, oracle_get_devices


def message_handler(dev):
    while True:
        new_message = mongo_get_message(dev.DEVICE_ID)
        if new_message:
            response = device_request(new_message.URI)
            new_message.REQUEST_DATE = datetime.now()
            new_message.RESPONSE_BODY = response['response_body']
            new_message.RESPONSE_CODE = response['response_code']
            new_message.MESSAGE_STATE_ID = 21 if new_message.RESPONSE_CODE == 200 else 24
            new_message.RESPONSE_DATE = datetime.now()
            message_updated = False
            while not message_updated:
                try:
                    new_message.save()
                except Exception as ee:
                    print(ee)
                else:
                    message_updated = True


def start_processes(devices):
    try:
        processes_list = [Process(target=message_handler, args=(d,)) for d in devices]
    except TypeError as exc:
        print(exc)
    else:
        for p in processes_list:
            p.start()
        print(f'{len(processes_list)} processes started...')
        return processes_list


if __name__ == '__main__':
    processes = start_processes(oracle_get_devices())
    print(f'Started {len(processes)} processes')
    while True:
        for proc in processes:
            if not proc.is_alive():
                exit()
        mongo_done_messages = mongo_get_done_messages()
        for message in mongo_done_messages:
            if oracle_update_message(message):
                mongo_delete_message(message)
        oracle_new_messages = oracle_get_new_messages()
        if not oracle_new_messages:
            sleep(3)
            continue
        mongo_messages = mongo_get_messages()
        oracle_messages_not_in_mongo = list()
        for message in oracle_new_messages:
            if not list(filter(lambda x: x.DEVICE_ID <= message.DEVICE_ID, mongo_messages)):
                oracle_messages_not_in_mongo.append(message)
        for message in oracle_messages_not_in_mongo:
            try:
                mongo_insert_message(message)
            except Exception as e:
                print(e)
