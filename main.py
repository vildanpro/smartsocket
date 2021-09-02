import os
import json
from datetime import datetime
from multiprocessing import Process
from time import sleep

import cx_Oracle
import requests
from loguru import logger

import config


logger.add(f"{os.getcwd()}/main.log", rotation="1 week", enqueue=True)


def make_dict_factory(cursor):
    column_names = [d[0] for d in cursor.description]

    def create_row(*args):
        return dict(zip(column_names, args))

    return create_row


def execute_query(query, update=None):
    try:
        connection = cx_Oracle.connect(
            config.username,
            config.password,
            config.dsn,
            encoding=config.encoding
        )
    except Exception as e:
        logger.exception("What?!")
        print(e, '\n', 'connection exception!')
        return None
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        data = None
        if not cursor:
            return None
        if not update:
            cursor.rowfactory = make_dict_factory(cursor)
            data = cursor.fetchall()
        else:
            connection.commit()
        cursor.close()
        connection.close()
        return data
    except Exception as e:
        logger.exception("What?!")
        print(e, '\n', 'execute exception!')


def device_request(message, process_id):
    response_data = {'message_id': message['MESSAGE_ID'],
                     'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    print_message = f"DEVICE_ID: {message['DEVICE_ID']}, MESSAGE_ID: {message['MESSAGE_ID']}, URI: {message['URI']}"
    try:
        with requests.get(message['URI'], timeout=(30, 30)) as resp:
            response_data.update({'response_code': resp.status_code,
                                  'response_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  'response_body': json.dumps(resp.json())})
            query = "UPDATE sockets.messages\n" \
                    "SET message_state_id = 21,\n" \
                    "\tresponse_code = {response_code},\n" \
                    "\tresponse_body = '{response_body}',\n" \
                    "\trequest_date = TO_DATE(\'{request_date}\', 'YYYY-MM-DD HH24:MI:SS'),\n" \
                    "\tresponse_date = TO_DATE('{response_date}', 'YYYY-MM-DD HH24:MI:SS')\n" \
                    "WHERE message_id = {message_id}".format(**response_data)
            execute_query(query, update=True)
            print(print_message, f'\nPROCESS ID {process_id}: Success')
            return response_data
    except Exception as e:
        logger.exception("What?!")
        response_data.update({'response_code': 408,
                              'response_body': json.dumps({'Exception': str(e).replace("'", '')})})
        query = "UPDATE sockets.messages\n" \
                "SET message_state_id = 24,\n" \
                "\tresponse_code = {response_code},\n" \
                "\tresponse_body = '{response_body}',\n" \
                "\trequest_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS')\n" \
                "WHERE message_id = {message_id}".format(**response_data)
        execute_query(query, update=True)
        return response_data


def device_process(device_id, process_id):
    while True:
        query = f"SELECT * FROM sockets.messages WHERE message_state_id = 1 AND device_id = {device_id} AND rownum = 1"
        message = execute_query(query)
        message = message[0] if message else message
        if message:
            device_request(message, process_id)
        sleep(3)


if __name__ == '__main__':
    for i, device in enumerate(execute_query('SELECT * FROM sockets.devices ORDER BY device_id')):
        p = Process(target=device_process, args=(device['DEVICE_ID'], i))
        p.start()
        sleep(1)
