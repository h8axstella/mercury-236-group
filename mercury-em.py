#!.env/bin/python3.9
# -*- coding: utf-8 -*-

import socket
import json
import configparser
import mercury.mercury236 as mercury236

def read_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        'serial': config.getint('Settings', 'serial', fallback=0),
        'host': config.get('Settings', 'host', fallback='0'),
        'port': config.getint('Settings', 'port', fallback=50),
        'user': config.get('Settings', 'user', fallback='user'),
        'passwd': config.get('Settings', 'passwd', fallback=''),
        'format': config.get('Settings', 'format', fallback='json'),
    }

def print_output(arr, output_format):
    if output_format == "json":
        print(json.dumps(arr, indent=4))

if __name__ == "__main__":
    args = read_config()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((args['host'], args['port']))

        serial = args['serial']
        user = args['user']
        passwd = args['passwd']

        mercury236.check_connect(sock, serial)
        mercury236.open_channel(sock, serial, user, passwd)

        result = {
            'vap': mercury236.read_vap(sock, serial),
            'energy': mercury236.read_energy(sock, serial),
            'energy_beginning_of_month': mercury236.read_energy_beginning_of_month(sock, serial),
            'freq': mercury236.read_freq(sock, serial),
            'energy_sum_by_phases': mercury236.read_energy_sum_by_phases(sock, serial),
            'energy_tarif_by_phases': mercury236.read_energy_tarif_by_phases(sock, serial),
        }

        mercury236.close_channel(sock, serial)
    except Exception as e:
        result = {'error': str(e)}
    finally:
        sock.close()

    print_output(result, args['format'])
