from multiprocessing import Process
from time import sleep
from datetime import datetime
import requests
import json
from sqlite import Session, MessageModel
from oracle import get_devices, get_new_oracle_messages, oracle_update_message


time_to_sleep = 1


def process_func(device_id):
    while True:
        s = Session()
        try:
            m = s.query(MessageModel).filter_by(DEVICE_ID=device_id, MESSAGE_STATE_ID=1).first()
            if not m:
                sleep(time_to_sleep)
                continue
        except Exception as ex:
            print('process_func -> get message', ex)
            sleep(time_to_sleep)
        else:
            dt = datetime.now()
            try:
                response = None
                try:
                    response = requests.get(m.URI, timeout=(30, 30))
                    m.RESPONSE_BODY = json.dumps(response.json())
                except Exception as e:
                    m.RESPONSE_BODY = json.dumps({'Exception': str(e).replace("'", '')})
                m.MESSAGE_STATE_ID = 21 if response else 24
                m.RESPONSE_CODE = 200 if response else 408
                m.REQUEST_DATE = m.RESPONSE_DATE = dt
            except Exception:
                sleep(time_to_sleep)
            message_updated = False
            while not message_updated:
                try:
                    s.add(m)
                    s.commit()
                except Exception as ee:
                    print('sqlite message update', ee)
                else:
                    message_updated = True


if __name__ == '__main__':
    print('Start Tasmota script')
    while True:
        try:
            processes_list = [Process(target=process_func, args=(device.DEVICE_ID,)) for device in get_devices()]
            print(f'{len(processes_list)} processes')
        except TypeError as e:
            print('processes_list: no devices')
            continue
        else:
            for process in processes_list:
                process.start()
            print('Processes started...')
        while True:
            try:
                session = Session()
                exist = False
                for oracle_message in get_new_oracle_messages():
                    sqlite_messages = session.query(MessageModel).filter_by(DEVICE_ID=oracle_message.DEVICE_ID).all()
                    for sqlite_message in sqlite_messages:
                        if sqlite_message.MESSAGE_ID < oracle_message.MESSAGE_ID:
                            session.delete(sqlite_message)
                        elif oracle_message.MESSAGE_ID == sqlite_message.MESSAGE_ID:
                            exist = True
                    if not exist:
                        session.add(MessageModel(
                            MESSAGE_ID=oracle_message.MESSAGE_ID,
                            MESSAGE_TYPE_ID=oracle_message.MESSAGE_TYPE_ID,
                            DEVICE_ID=oracle_message.DEVICE_ID,
                            MESSAGE_STATE_ID=oracle_message.MESSAGE_STATE_ID,
                            URI=oracle_message.URI,
                            RESPONSE_CODE=oracle_message.RESPONSE_CODE,
                            RESPONSE_BODY=oracle_message.RESPONSE_BODY,
                            REQUEST_DATE=oracle_message.REQUEST_DATE,
                            RESPONSE_DATE=oracle_message.RESPONSE_DATE)
                        )
                sqlite_done_messages = session.query(MessageModel).filter(MessageModel.MESSAGE_STATE_ID != 1).all()
                for sqlite_message in sqlite_done_messages:
                    try:
                        oracle_update_message(sqlite_message)
                    except Exception as e:
                        print('main -> oracle_update_message:', e)
                    else:
                        session.delete(sqlite_message)
                session.commit()
                session.close()
            except Exception as e:
                print(e)
            sleep(time_to_sleep)
