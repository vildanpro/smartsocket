import routeros_api
import config


def get_dhcp_leases():
    try:
        connection = routeros_api.RouterOsApiPool(config.mikrotik_ip,
                                                  username=config.mikrotik_username,
                                                  password=config.mikrotik_password,
                                                  plaintext_login=True)
        api = connection.get_api()
        leases = api.get_resource('/ip/dhcp-server/lease/').get()
        bound_leases = list()
        for lease in leases:
            if lease['status'] == 'bound' and int(lease['address'].split('.')[3]) >= 100:
                bound_leases.append(lease)
        return 0 if not bound_leases else bound_leases
    except Exception as e:
        print(e)
        return 'No connection'


def remove_dhcp_lease(lease_id):
    try:
        connection = routeros_api.RouterOsApiPool(config.mikrotik_ip,
                                                  username=config.mikrotik_username,
                                                  password=config.mikrotik_password,
                                                  plaintext_login=True)
        api = connection.get_api()
        remove_lease = api.get_resource(f'/ip/dhcp-server/lease/remove/{lease_id}').get()
        print(remove_lease)
    except Exception as e:
        print(e)
        return 'No connection'

