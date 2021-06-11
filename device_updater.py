from time import sleep
from queries import update_device_ip, select_device, insert_device
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
            device_db = select_device(lease['MAC'])
            if device_db:
                if device_db[0]['IP'] != lease['IP']:
                    update_device_ip(device_db[0]['MAC'], lease['IP'])
                    print(f'Updated device {device_db[0]["DEVICE_NAME"]}')
            else:
                insert_device(mac=lease['mac'], ip=lease['ip'])
        sleep(5)

