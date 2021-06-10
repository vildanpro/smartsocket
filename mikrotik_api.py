import routeros_api
import config


def get_dhcp_leases():
    connection = routeros_api.RouterOsApiPool(config.mikrotik_ip,
                                              username=config.mikrotik_username,
                                              password=config.mikrotik_password,
                                              plaintext_login=True)
    api = connection.get_api()
    return api.get_resource('/ip/dhcp-server/lease/').get()
