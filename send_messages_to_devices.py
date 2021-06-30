from db import insert_new_message, select_device_by_mac, get_messages_types
from mikrotik_api import get_dhcp_leases
import sys
from pprint import pprint


def add_messages(leases, message_type_id):
    devices = list()
    for lease in leases:
        devices.append(select_device_by_mac(lease['mac-address']))
    for i, device in enumerate(devices, start=1):
        insert_new_message(device_id=device['DEVICE_ID'],
                           message_type_id=message_type_id)
        print(f'{i}. Insert message: device_id {device["DEVICE_ID"]}, message_type_id {message_type_id}')


if __name__ == '__main__':
    message_types_id = get_messages_types()
    if not message_types_id:
        print('No states, exit.')
    pprint(message_types_id)
    message_type_id = input('Выберите тип соообщения для устройств: ')
    add_messages(get_dhcp_leases(), message_type_id)
