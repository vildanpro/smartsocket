from db import update_device_upper_mac, get_devices


devices_db = get_devices()

for device in devices_db:
    update_device_upper_mac(device.mac)
