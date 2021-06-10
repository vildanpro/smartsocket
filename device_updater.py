import subprocess
from time import sleep

from queries import update_device_ip, select_device, insert_device
from mikrotik_api import get_dhcp_leases


def clean_leases(leases_list):
    leases_cleaned = list()
    for lease_raw in leases_list:
        if int(lease_raw['address'].split('.')[3]) >= 100:
            leases_cleaned.append({'mac': lease_raw['mac-address'].upper(), 'ip': lease_raw['address']})
    return leases_cleaned


if __name__ == '__main__':
    while True:
        leases_raw = get_dhcp_leases()
        leases = clean_leases(leases_raw)
        while leases:
            lease = leases.pop()
            device_db = select_device(lease['mac'])
            if device_db:
                if device_db[0].ip != lease['ip']:
                    update_device_ip(device_db[0].mac, lease['ip'])
                    print(f'Updated device {device_db[0].device_name}')
            else:
                insert_device(mac=lease['mac'], ip=lease['ip'])
        sleep(5)

