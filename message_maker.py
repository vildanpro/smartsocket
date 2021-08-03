from random import choice
from collections import namedtuple
from time import sleep

from db import DB
from device_updater import get_dhcp_leases, clean_leases

db = DB()
sleep_sec = 0
random_id = False
only_online = True
ids = []
new_message = namedtuple('Message', ['message_type_id', 'device_id', 'message_state_id'])
message_types = [41]

while True:
    if ids:
        print('Генерация по указаынм ID:', ids)
        devices = db.select_devices_by_id(ids)
        db.insert_new_message(device_id=choice(devices)['DEVICE_ID'],
                              message_type_id=choice(message_types),
                              message_state_id=1)
    else:
        if only_online:
            print('Генерация только по устройствам которые online...')
            leases = get_dhcp_leases()
            devices = list()
            for lease in leases:
                device = db.select_device_by_mac(lease['mac-address'])
                devices.append(device)
        else:
            devices = db.select_devices_ids()
        if random_id:
            print('Выбрана случайная выборка устройств...')
            for device in devices:
                print(device)
                db.insert_new_message(device_id=choice(devices)['DEVICE_ID'],
                                      message_type_id=choice(message_types),
                                      message_state_id=1)
        elif not random_id:
            print('Выбрана последовательная выборка устройств...')
            for device in devices:
                print(device)
                db.insert_new_message(device_id=device['DEVICE_ID'],
                                      message_type_id=choice(message_types),
                                      message_state_id=1)
    print(f'Done. Wait {sleep_sec} seconds...')
    sleep(sleep_sec)
