from db import DB

db = DB()


def add_messages(leases, message_type_id):
    devices = list()
    for lease in leases:
        devices.append(db.select_device_by_mac(lease['mac-address']))
    for i, device in enumerate(devices, start=1):
        db.insert_new_message(device_id=device['DEVICE_ID'],
                              message_type_id=message_type_id)
        print(f'{i}. Insert message: device_id {device["DEVICE_ID"]}, message_type_id {message_type_id}')


def add_message(device, message_type_id):
    db.insert_new_message(device_id=device['DEVICE_ID'],
                          message_type_id=message_type_id)
    print(f'Insert message: device_id {device["DEVICE_ID"]}, message_type_id {message_type_id}')


if __name__ == '__main__':
    message_types_id = db.get_messages_types()
    if not message_types_id:
        print('No states, exit.')
    for message_type in message_types_id:
        print(message_type['MESSAGE_TYPE_ID'], message_type['DESCRIPTION'])
    message_type_id = input('\nВыберите тип соообщения для устройств: ')
    add_messages(get_dhcp_leases(), message_type_id)
