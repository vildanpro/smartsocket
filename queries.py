import collections
import cx_Oracle
import config


def read_sql_file(filename):
    path = f'sql/{filename}'
    with open(path) as f:
        sql_file = f.readlines()
        sql = ''.join(sql_file)
    return sql


def make_named_tuple_factory(cursor):
    column_names = [d[0].lower() for d in cursor.description]
    row = collections.namedtuple('row', column_names)
    return row


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
    cursor = connection.cursor().execute(query)
    cursor.rowfactory = make_named_tuple_factory(cursor)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data


def query_insert(query):
    connection = get_oracle_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()


def query_update(query):
    connection = get_oracle_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()


def get_new_messages():
    return query_select('SELECT * FROM sockets.messages WHERE message_state_id = 1 ORDER BY message_id')


def get_devices():
    return query_select('SELECT * FROM sockets.devices ORDER BY device_id')


def update_message_if_response_code_200(data):
    sql = """
                UPDATE sockets.messages
                SET message_state_id = 21,
                    response_code = 200,
                    response_body = '{response_body}',
                    request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS'),
                    response_date = TO_DATE('{response_date}', 'YYYY-MM-DD HH24:MI:SS')
                WHERE message_id = {message_id}
    """.format(**data)
    query_update(sql)


def update_message_with_exception(data):
    sql = """
                UPDATE sockets.messages
                SET message_state_id = 24, response_code = {response_code}, response_body = '{response_body}',
                    request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS')
                WHERE message_id = {message_id}
    """.format(**data)
    query_update(sql)


def insert_new_message(message):
    sql = read_sql_file('insert_message.sql')
    query_insert(sql.format(message_type_id=message.message_type_id,
                            device_id=message.device_id,
                            message_state_id=message.message_state_id))


def update_new_ip(device_id, device_ip):
    sql_template = read_sql_file('update_new_ip.sql')
    sql_query = sql_template.format(id=device_id, ip=device_ip)
    query_update(sql_query)


def select_devices_ids():
    sql = read_sql_file('select_devices_ids.sql')
    return query_select(sql)


def select_devices_by_id(ids):
    devices = []
    for device_id in ids:
        sql = f"""
            SELECT *
            FROM SOCKETS.DEVICES
            WHERE DEVICE_ID = {device_id}
            """
        device = query_select(sql)
        devices.append(device[0])
    return devices


def select_devices_names():
    sql = read_sql_file('select_devices_names.sql')
    return query_select(sql)


def select_device(mac):
    sql = read_sql_file('select_device.sql').format(mac=mac.upper())
    return query_select(sql)


def update_device_upper_mac(mac):
    sql = read_sql_file('update_upper_mac.sql')
    query_update(sql.format(mac=mac, mac_upper=mac.upper()))


def update_device_ip(mac, ip):
    sql = read_sql_file('update_device_ip.sql')
    query_update(sql.format(mac=mac.upper(), ip=ip))


def insert_device(mac, ip):
    print(mac, ip)
    device_names = select_devices_names()
    last_device_number = 0
    for device_name in device_names:
        device_number = int(''.join(filter(str.isdigit, device_name.device_name)))
        print('device number', device_number)
        if device_number and device_number > last_device_number:
            last_device_number = device_number
            print('last_device_number', last_device_number)
    device_name = f'S-{str(last_device_number + 1).zfill(4)}'
    print(device_name)
    sql = read_sql_file('insert_device.sql')
    query_insert(sql.format(device_name=device_name, mac=mac.upper(), ip=ip))
