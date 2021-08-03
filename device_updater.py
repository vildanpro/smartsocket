from time import sleep
from db import DB
from mikrotik_api import get_dhcp_leases, remove_dhcp_lease
import socket
import requests


db = DB()


def ping_server(server: str, port: int, timeout=1):
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
        leases_cleaned.append({'MAC': les['mac-address'].upper(), 'IP': les['address'], 'ID': les['id']})
    return leases_cleaned


if __name__ == '__main__':
    sec = 10
    while True:
        leases_raw = get_dhcp_leases()
        if not leases_raw:
            print(f'no leases, repeat, wait {sec}...')
            sleep(sec)
            continue
        leases = clean_leases(leases_raw)

        if not leases:
            print(f'No leases, wait {sec} seconds...')
        else:
            while leases:
                lease = leases.pop()
                device_db = db.select_device_by_mac(lease['MAC'])
                if device_db:
                    if device_db['IP'] != lease['IP']:
                        r = requests.get(f'http://{lease["IP"]}/cm?cmnd=IPAddress1%20{device_db["IP"]}')
                        print(r.text)
                        r = requests.get(f'http://{lease["IP"]}/cm?cmnd=restart%201')
                        print(r.text)
                        # remove_dhcp_lease(lease['ID'])
                        print(f'Device {device_db["DEVICE_NAME"]} updated {lease["IP"]} -> {device_db["IP"]}')
            print(f'No updates, waiting {sec} seconds...')
        sleep(10)
