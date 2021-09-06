import os
import json
from datetime import datetime
from multiprocessing import Process
from time import sleep
import requests
from loguru import logger
from sqlite_db import sqlite_insert_oracle_messages, sqlite_get_message, sqlite_update_message,\
    sqlite_get_processed_messages, sqlite_remove_message
from oracle_db import execute_query

logger.add(f"{os.getcwd()}/main.log", rotation="1 week", format="{time} {level} {message}", enqueue=True)


def device_request(message, process_id):
    request_date = datetime.now()
    print_message = f"DEVICE_ID: {message.DEVICE_ID}, MESSAGE_ID: {message.MESSAGE_ID}, URI: {message.URI}"
    message_update = None
    try:
        with requests.get(message.URI, timeout=(30, 30)) as resp:
            message.MESSAGE_STATE_ID = 21
            message.REQUEST_DATE = request_date
            message.RESPONSE_CODE = resp.status_code
            message.RESPONSE_DATE = datetime.now()
            message.RESPONSE_BODY = json.dumps(resp.json())
        if not message_update:
            while not message_update:
                message_update = sqlite_update_message(message)
        print(print_message, f'\nPROCESS ID {process_id}: Success')
    except Exception as e:
        logger.exception("What?!")
        message.MESSAGE_STATE_ID = 24
        message.RESPONSE_CODE = 408
        message.RESPONSE_BODY = json.dumps({'Exception': str(e).replace("'", '')})
        message.REQUEST_DATE = request_date
        if not message_update:
            while not message_update:
                message_update = sqlite_update_message(message)
        print(print_message, f'\nPROCESS ID {process_id}: Success')


def device_process(device_id, process_id):
    while True:
        message = sqlite_get_message(device_id)
        if message:
            device_request(message, process_id)
        sleep(1)


def message_manager():
    print('MESSAGE MANAGER STARTED...')
    sleep(3)
    while True:
        sqlite_messages_processed = sqlite_get_processed_messages()
        if sqlite_messages_processed:
            for sqlite_message_processed in sqlite_messages_processed:
                if sqlite_message_processed.RESPONSE_CODE == 200:
                    query = f"UPDATE sockets.messages\n" \
                            f"SET message_state_id = {sqlite_message_processed.MESSAGE_STATE_ID},\n" \
                            f"\tresponse_code = {sqlite_message_processed.RESPONSE_CODE},\n" \
                            f"\tresponse_body = '{sqlite_message_processed.RESPONSE_BODY}',\n" \
                            f"\trequest_date = TO_DATE(\'{sqlite_message_processed.REQUEST_DATE}\', 'YYYY-MM-DD HH24:MI:SS'),\n" \
                            f"\tresponse_date = TO_DATE('{sqlite_message_processed.RESPONSE_DATE}', 'YYYY-MM-DD HH24:MI:SS')\n" \
                            f"WHERE message_id = {sqlite_message_processed.MESSAGE_ID}"
                    execute_query(query, result=True)
                elif sqlite_message_processed.RESPONSE_CODE == 408:
                    query = f"UPDATE sockets.messages\n" \
                            f"SET message_state_id = {sqlite_message_processed.MESSAGE_STATE_ID},\n" \
                            f"\tresponse_code = {sqlite_message_processed.RESPONSE_CODE},\n" \
                            f"\tresponse_body = '{sqlite_message_processed.RESPONSE_BODY}',\n" \
                            f"\trequest_date = TO_DATE('{sqlite_message_processed.REQUEST_DATE}', 'YYYY-MM-DD HH24:MI:SS')\n" \
                            f"WHERE message_id = {sqlite_message_processed.MESSAGE_ID}"
                    execute_query(query, result=True)
                result = False
                while not result:
                    result = sqlite_remove_message(sqlite_message_processed)

        query = 'SELECT m.MESSAGE_ID, m.MESSAGE_TYPE_ID, m.DEVICE_ID, m.MESSAGE_STATE_ID, m.URI, m.RESPONSE_CODE,\n' \
                '\t\tm.RESPONSE_BODY, m.REQUEST_DATE, m.RESPONSE_DATE\n' \
                'FROM (SELECT DEVICE_ID, MIN(MESSAGE_ID) AS MESSAGE_ID\n' \
                '\t\tFROM MESSAGES\n' \
                '\t\tWHERE MESSAGE_STATE_ID = 1\n' \
                '\t\tGROUP BY DEVICE_ID) n\n' \
                'JOIN MESSAGES m\n' \
                'ON n.MESSAGE_ID = m.MESSAGE_ID'
        oracle_messages = execute_query(query)
        sqlite_insert_oracle_messages(oracle_messages)


def create_process(device_data, device_index):
    p = Process(target=device_process, args=(device_data['DEVICE_ID'], device_index))
    p.start()


if __name__ == '__main__':
    message_manager_process = Process(target=message_manager)
    message_manager_process.start()

    processes_dict = dict()
    for i, device in enumerate(execute_query('SELECT * FROM sockets.devices ORDER BY device_id')):
        processes_dict[i] = Process(target=device_process, args=(device['DEVICE_ID'], i))

    print('START DEVICE PROCESSES...')
    for process in processes_dict.values():
        process.start()
    print(len(processes_dict), '- PROCESSES STARTED!')
    while True:
        sleep(30)
        print('CHECK PROCESSES...')
        for process_id, process in processes_dict.items():
            print(process_id, process.is_alive())
            if not process.is_alive():
                print(f'PROCESS {process_id} is not alive, restarting...')
                process.start()
                print(f'PROCESS {process_id} started...')
        print('PROCESSES CHECKED!')
