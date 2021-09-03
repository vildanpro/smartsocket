import os
import cx_Oracle
import config
from loguru import logger


logger.add(f"{os.getcwd()}/main.log", rotation="1 week", format="{time} {level} {message}", enqueue=True)


def make_dict_factory(cursor):
    column_names = [d[0] for d in cursor.description]

    def create_row(*args):
        return dict(zip(column_names, args))

    return create_row


def execute_query(query, result=None):
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
        elif not result:
            cursor.rowfactory = make_dict_factory(cursor)
            data = cursor.fetchall()
        elif result:
            connection.commit()
        cursor.close()
        connection.close()
        return data
    except Exception as e:
        logger.exception("What?!")
        print(e, '\n', 'execute exception!')
