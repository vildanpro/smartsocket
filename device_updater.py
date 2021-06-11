from time import sleep
from queries import update_device_ip, select_device_by_mac, insert_device
from mikrotik_api import get_dhcp_leases


def clean_leases(leases_list):
    leases_cleaned = list()
    for lease_raw in leases_list:
        if int(lease_raw['address'].split('.')[3]) >= 100:
            leases_cleaned.append({'MAC': lease_raw['mac-address'].upper(), 'IP': lease_raw['address']})
    return leases_cleaned


if __name__ == '__main__':
    while True:
        leases_raw = get_dhcp_leases()
        if not leases_raw:
            print('sw not connected, repeat...')
            continue
        leases = clean_leases(leases_raw)
        while leases:
            lease = leases.pop()
            device_db = select_device_by_mac(lease['MAC'])
            if device_db:
                if device_db['IP'] != lease['IP']:
                    update_device_ip(device_db['MAC'], lease['IP'])
            else:
                insert_device(mac=lease['MAC'], ip=lease['IP'])
        sleep(5)

