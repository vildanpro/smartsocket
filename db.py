import cx_Oracle
import config
from datetime import datetime


def make_dict_factory(cursor):
    column_names = [d[0] for d in cursor.description]

    def create_row(*args):
        return dict(zip(column_names, args))

    return create_row


class DB:
    def __init__(self):
        self.wait_connection = 5
        self.connection = None
        while not self.connection:
            try:
                self.connection = cx_Oracle.connect(
                    config.username,
                    config.password,
                    config.dsn,
                    encoding=config.encoding
                )
            except cx_Oracle.Error as error:
                print(error, f'\nWait {self.wait_connection} seconds...')

    def select(self, query):
        if self.connection:
            try:
                with self.connection.cursor().execute(query) as cursor:
                    cursor.rowfactory = make_dict_factory(cursor)
                    data = cursor.fetchall()
                return data
            except Exception as e:
                print('def select():', e)
        print('DB not connected, reconnect...')
        self.__init__()

    def upsert(self, query):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(query)
                self.connection.commit()
                return True
            except Exception as e:
                print(query)
                print('def upsert():', e)

        print('DB not connected, reconnect...')
        self.__init__()

    def get_new_messages(self):
        return self.select('SELECT * FROM sockets.messages WHERE message_state_id = 1 ORDER BY message_id')

    def get_new_message(self, device_id):
        query = f"SELECT * FROM sockets.messages WHERE message_state_id = 1 AND device_id = {device_id} AND rownum = 1"
        print(query)
        return self.select(query)[0] if self.select(query) else None

    def get_messages_types(self):
        return self.select('SELECT * FROM sockets.message_types')

    def get_new_messages_by_device_id(self, device_id):
        return self.select(
            f'SELECT * FROM sockets.messages WHERE message_state_id = 1 and device_id = {device_id} ORDER BY message_id'
        )

    def get_devices(self):
        return self.select('SELECT * FROM sockets.devices ORDER BY device_id')

    def update_message_if_response_code_200(
            self,
            message_id,
            response_code,
            request_date,
            response_date,
            response_body
    ):
        self.upsert(f"""UPDATE sockets.messages
                        SET message_state_id = 21,
                            response_code = {response_code},
                            response_body = '{response_body}',
                            request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS'),
                            response_date = TO_DATE('{response_date}', 'YYYY-MM-DD HH24:MI:SS')
                        WHERE message_id = {message_id}""")

    def update_message_with_exception(self, message_id, response_code, response_body, request_date):
        sql = f"""UPDATE sockets.messages
                  SET message_state_id = 24,
                      response_code = {response_code},
                      response_body = '{response_body}',
                      request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS')
                  WHERE message_id = {message_id}"""
        return self.upsert(sql)

    def insert_new_message(self, device_id, message_type_id):
        return self.upsert(f'''INSERT INTO sockets.messages(message_type_id, device_id)
                               VALUES({message_type_id}, {device_id})''')

    def update_new_ip(self, device_id, device_ip):
        return self.upsert(f"UPDATE sockets.devices SET ip = '{device_ip}' WHERE device_id = {device_id}")

    def select_devices_ids(self):
        return self.select('SELECT device_id FROM sockets.devices')

    def select_devices_by_id(self, ids) -> list:
        devices = list()
        for device_id in ids:
            sql = f'SELECT * FROM SOCKETS.DEVICES WHERE DEVICE_ID = {device_id}'
            device = self.select(sql)
            devices.append(device[0])
        return devices

    def select_devices_names(self) -> list:
        return self.select(f'SELECT device_name FROM sockets.devices')

    def select_device_by_mac(self, mac):
        device = self.select(
            f"SELECT device_id, device_name, mac, ip FROM sockets.devices WHERE mac = '{mac.upper()}'")
        if device:
            return device[0]

    def update_device_upper_mac(self, mac):
        return self.upsert(f"UPDATE sockets.devices SET mac = '{mac.upper()}' WHERE mac = '{mac}'")

    def update_device_ip(self, mac, ip):
        return self.upsert(f"UPDATE sockets.devices SET ip = '{ip}' WHERE mac = '{mac.upper()}'")

    def insert_device(self, mac, ip):
        device_names = self.select_devices_names()
        last_device_number = 0
        for device_name in device_names:
            device_number = int(''.join(filter(str.isdigit, device_name['DEVICE_NAME'])))
            if device_number and device_number > last_device_number:
                last_device_number = device_number
        device_name = f'S-{str(last_device_number + 1).zfill(4)}'
        print(f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")} - New device added: {device_name}, {mac.upper()}, {ip}')
        return self.upsert(f"INSERT INTO sockets.devices(device_name, mac, ip) "
                           f"VALUES('{device_name}', '{mac.upper()}', '{ip}')")
