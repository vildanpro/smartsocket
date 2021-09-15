from time import sleep
import cx_Oracle
from oracle import credentials, get_devices


time_to_sleep = 10
loop = False
action = 22


def insert_new_message(device_id, message_type_id):
    query = f'INSERT INTO sockets.messages(message_type_id, device_id) VALUES({message_type_id}, {device_id})'
    try:
        connection = cx_Oracle.connect(**credentials)
        cursor = connection.cursor()
        cursor.execute(query)
    except Exception as e:
        print('insert_new_message', e)
    else:
        connection.commit()
        print(f'Inserted message: DEVICE_ID {device_id}, MESSAGE_TYPE_ID {message_type_id}')


if __name__ == '__main__':
    count = 0
    while True:
        for device in get_devices():
            insert_new_message(device.DEVICE_ID, action)
        if not loop:
            break
        sleep(time_to_sleep)
