from db import DB

db = DB()


def add_message(device, message_type_id):
    db.insert_new_message(device_id=device['DEVICE_ID'],
                          message_type_id=message_type_id)
    print(f'Insert message: device_id {device["DEVICE_ID"]}, message_type_id {message_type_id}')


if __name__ == '__main__':
    devices = db.get_devices()
    while True:
        for device in devices:
            add_message(device, '22')
        exit()
