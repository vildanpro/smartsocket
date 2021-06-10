import random
from collections import namedtuple
from time import sleep

from queries import insert_new_message, select_devices_ids, select_devices_by_id


ids = [42, 48]

new_message = namedtuple('Message', ['message_type_id', 'device_id', 'message_state_id'])
message_types = [41]
if not ids:
    devices = select_devices_ids()
else:
    devices = select_devices_by_id(ids)
while True:
    message = new_message(message_type_id=random.choice(message_types),
                          device_id=random.choice(devices).device_id,
                          message_state_id=1)
    insert_new_message(message)
    sleep(1)