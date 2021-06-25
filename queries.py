import cx_Oracle
import config
from datetime import datetime


def make_dict_factory(cursor):
    column_names = [d[0] for d in cursor.description]

    def create_row(*args):
        return dict(zip(column_names, args))
    return create_row


def get_oracle_connection():
    connection = None
    try:
        connection = cx_Oracle.connect(
            config.username,
            config.password,
            config.dsn,
            encoding=config.encoding)
    except cx_Oracle.Error as error:
        print(error)
    finally:
        if connection:
            return connection


def query_select(query):
    connection = get_oracle_connection()
    if connection:
        with connection.cursor().execute(query) as cursor:
            cursor.rowfactory = make_dict_factory(cursor)
            data = cursor.fetchall()
        connection.close()
        return data


def query_insert(query):
    connection = get_oracle_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        return True


def query_update(query):
    connection = get_oracle_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        return True


def get_new_messages():
    return query_select('SELECT * FROM sockets.messages WHERE message_state_id = 1 ORDER BY message_id')


def get_new_messages_by_device_id(device_id):
    return query_select(
        f'SELECT * FROM sockets.messages WHERE message_state_id = 1 and device_id = {device_id} ORDER BY message_id'
    )


def get_devices():
    return query_select('SELECT * FROM sockets.devices ORDER BY device_id')


def update_message_if_response_code_200(message_id, response_code, request_date, response_date, response_body):
    query_update(
        f"""
            UPDATE sockets.messages
            SET message_state_id = 21,
                response_code = {response_code},
                response_body = '{response_body}',
                request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS'),
                response_date = TO_DATE('{response_date}', 'YYYY-MM-DD HH24:MI:SS')
            WHERE message_id = {message_id}
        """
    )


def update_message_with_exception(message_id, response_code, response_body, request_date):
    sql = f"""
            UPDATE sockets.messages
            SET message_state_id = 24, response_code = {response_code}, response_body = '{response_body}',
                request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS')
            WHERE message_id = {message_id}
        """
    query_update(sql)


def insert_new_message(device_id, message_type_id, message_state_id):
    print(
        f'Insert message: device_id {device_id}, message_type_id {message_type_id}, message_state_id {message_state_id}'
    )
    query_insert(
        f'''
            INSERT INTO sockets.messages(message_type_id, device_id, message_state_id) 
            VALUES({message_type_id}, {device_id}, {message_state_id})
    ''')


def update_new_ip(device_id, device_ip):
    query_update(f"UPDATE sockets.devices SET ip = '{device_ip}' WHERE device_id = {device_id}")


def select_devices_ids():
    return query_select('SELECT device_id FROM sockets.devices')


def select_devices_by_id(ids) -> list:
    devices = list()
    for device_id in ids:
        sql = f'SELECT * FROM SOCKETS.DEVICES WHERE DEVICE_ID = {device_id}'
        device = query_select(sql)
        devices.append(device[0])
    return devices


def select_devices_names() -> list:
    return query_select(f'SELECT device_name FROM sockets.devices')


def select_device_by_mac(mac):
    device = query_select(f"SELECT device_id, device_name, mac, ip FROM sockets.devices WHERE mac = '{mac.upper()}'")
    if device:
        return device[0]


def update_device_upper_mac(mac):
    query_update(f"UPDATE sockets.devices SET mac = '{mac.upper()}' WHERE mac = '{mac}'")


def update_device_ip(mac, ip):
    device = select_device_by_mac(mac)
    query_update(f"UPDATE sockets.devices SET ip = '{ip}' WHERE mac = '{mac.upper()}'")


def insert_device(mac, ip):
    device_names = select_devices_names()
    last_device_number = 0
    for device_name in device_names:
        device_number = int(''.join(filter(str.isdigit, device_name['DEVICE_NAME'])))
        if device_number and device_number > last_device_number:
            last_device_number = device_number
    device_name = f'S-{str(last_device_number + 1).zfill(4)}'
    print(f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")} - New device added: {device_name}, {mac.upper()}, {ip}')
    query_insert(f"INSERT INTO sockets.devices(device_name, mac, ip) VALUES('{device_name}', '{mac.upper()}', '{ip}')")
