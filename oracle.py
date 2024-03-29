from collections import namedtuple
import cx_Oracle
from config import oracle_credentials
from sql_queries import get_query_devices, get_query_new_oracle_messages, get_query_update_message


def make_namedtuple_factory(cursor):
    column_names = [d[0] for d in cursor.description]
    row = namedtuple('Row', column_names)
    return row


def get_devices():
    query = get_query_devices()
    try:
        connection = cx_Oracle.connect(**oracle_credentials)
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.rowfactory = make_namedtuple_factory(cursor)
    except Exception as e:
        print('get_devices', e)
    else:
        data = cursor.fetchall()
        connection.close()
        return data


def get_new_oracle_messages():
    query = get_query_new_oracle_messages()
    try:
        connection = cx_Oracle.connect(**oracle_credentials)
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.rowfactory = make_namedtuple_factory(cursor)
    except Exception as e:
        print('get_new_oracle_messages', e)
    else:
        data = cursor.fetchall()
        connection.close()
        return data


def oracle_update_message(message):
    query = get_query_update_message(message)
    try:
        connection = cx_Oracle.connect(**oracle_credentials)
        cursor = connection.cursor()
        cursor.execute(query)
        # cursor.rowfactory = make_namedtuple_factory(cursor)
        # cursor.fetchall()
    except Exception as e:
        print('oracle -> oracle_update_message', e)
    else:
        connection.commit()
        connection.close()
