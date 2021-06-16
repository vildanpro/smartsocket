from random import choice
from collections import namedtuple
from time import sleep

from queries import insert_new_message, select_devices_ids, select_devices_by_id, select_device_by_mac
from device_updater import get_dhcp_leases, clean_leases

sleep_sec = 30

random_id = False

only_online = True

ids = []

new_message = namedtuple('Message', ['message_type_id', 'device_id', 'message_state_id'])
message_types = [41]

while True:
    if ids:
        print('Генерация по указаынм ID:', ids)
        devices = select_devices_by_id(ids)
        insert_new_message(device_id=choice(devices)['DEVICE)ID'],
                           message_type_id=choice(message_types),
                           message_state_id=1)
    else:
        if only_online:
            print('Генерация только по устройствам которые online...')
            leases = clean_leases(get_dhcp_leases())
            devices = list()
            for lease in leases:
                device = select_device_by_mac(lease['MAC'])
                devices.append(device)
        else:
            devices = select_devices_ids()
        if random_id:
            print('Выбрана случайная выборка устройств...')
            for device in devices:
                print(device)
                insert_new_message(device_id=choice(devices)['DEVICE_ID'],
                                   message_type_id=choice(message_types),
                                   message_state_id=1)
        elif not random_id:
            print('Выбрана последовательная выборка устройств...')
            for device in devices:
                print(device)
                insert_new_message(device_id=device['DEVICE_ID'],
                                   message_type_id=choice(message_types),
                                   message_state_id=1)
    print(f'Done. Wait {sleep_sec} seconds...')
    sleep(sleep_sec)
