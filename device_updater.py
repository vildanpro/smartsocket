from time import sleep
from db import update_device_ip, select_device_by_mac, insert_device
from mikrotik_api import get_dhcp_leases
import socket


def ping_server(server: str, port: int, timeout=3):
    """ping server"""
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
    except OSError as error:
        return False
    else:
        s.close()
        return True


def clean_leases(leases_list):
    leases_cleaned = list()
    for les in leases_list:
        leases_cleaned.append({'MAC': les['mac-address'].upper(), 'IP': les['address']})
    return leases_cleaned


if __name__ == '__main__':
    sec = 10
    while True:
        leases_raw = get_dhcp_leases()
        if not leases_raw:
            print('sw not connected, repeat...')
            continue
        leases = clean_leases(leases_raw)
        if not leases:
            print(f'No leases, wait {sec} seconds...')
        else:
            while leases:
                lease = leases.pop()
                device_db = select_device_by_mac(lease['MAC'])
                if device_db:
                    if device_db['IP'] != lease['IP']:
                        update_device_ip(device_db['MAC'], lease['IP'])
                        print(f'Device {device_db["DEVICE_NAME"]} updated {device_db["IP"]} -> {lease["IP"]}')
                else:
                    insert_device(mac=lease['MAC'], ip=lease['IP'])

            print(f'No updates, waiting {sec} seconds...')
        sleep(10)


