from queries import insert_new_message, select_device_by_mac
from mikrotik_api import get_dhcp_leases
from pprint import pprint

leases = get_dhcp_leases()
devices = list()
for lease in leases:
    devices.append(select_device_by_mac(lease['mac-address']))
for device in devices:
    insert_new_message(device_id=device['DEVICE_ID'],
                       message_type_id=21,
                       message_state_id=1)

