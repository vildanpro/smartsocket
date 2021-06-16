from queries import insert_new_message, select_devices_ids


devices = select_devices_ids()
for device in devices:
    insert_new_message(device_id=device['DEVICE_ID'],
                       message_type_id=21,
                       message_state_id=1)

