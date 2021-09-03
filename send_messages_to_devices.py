from time import sleep
from oracle_db import execute_query


def insert_new_message(device_id, message_type_id):
    query = f'INSERT INTO sockets.messages(message_type_id, device_id) VALUES({message_type_id}, {device_id})'
    print(query)
    execute_query(query, result=True)
    print(f'Insert message: device_id {device_id}, message_type_id {message_type_id}')


if __name__ == '__main__':
    devices = execute_query('SELECT * FROM sockets.devices ORDER BY device_id')
    while True:
        for device in devices:
            insert_new_message(device['DEVICE_ID'], 41)
        sleep(30)
