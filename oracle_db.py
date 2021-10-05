import cx_Oracle
from config import oracle_credentials
from sql_queries import get_query_devices, get_query_new_oracle_messages, get_query_update_message
from addons import make_namedtuple_factory


def oracle_request(query, update=False):
    try:
        connection = cx_Oracle.connect(**oracle_credentials)
        cursor = connection.cursor()
        cursor.execute(query)
        if not update:
            cursor.rowfactory = make_namedtuple_factory(cursor)
            return cursor.fetchall()
        else:
            connection.commit()
            return True
    except Exception as e:
        print(e)


def oracle_get_devices():
    return oracle_request(get_query_devices())


def oracle_get_new_messages():
    return oracle_request(get_query_new_oracle_messages())


def oracle_update_message(message):
    return oracle_request(get_query_update_message(message), update=True)
