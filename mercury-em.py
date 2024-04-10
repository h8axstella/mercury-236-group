#!.env/bin/python3.9
# -*- coding: utf-8 -*-
#
# Mercury Energy Meter
#
# receive data from electricity meter MERCURY
#
# 2019 <eugene@skorlov.name>
#

import argparse
import socket
import json
import configparser
import mercury.mercury236 as mercury236

def read_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        'proto': config.get('Settings', 'proto', fallback='m206'),
        'serial': config.getint('Settings', 'serial', fallback=0),
        'host': config.get('Settings', 'host', fallback='0'),
        'port': config.getint('Settings', 'port', fallback=50),
        'user': config.get('Settings', 'user', fallback='user'),
        'passwd': config.get('Settings', 'passwd', fallback=''),
        'format': config.get('Settings', 'format', fallback='json'),
        'user_access_level': config.getint('Settings', 'user_access_level')
    }

    
def print_output_text(arr, prefix=""):
    for key, value in arr.items():
        if isinstance(value, dict):
            print_output_text(value, prefix + "." + key)
        else:
            print(f"{prefix}.{key}={value}")


def print_output(arr, output_format):
    if output_format == "text":
        print_output_text(arr)
    elif output_format == "json":
        print(json.dumps(arr, indent=4)) 


if __name__ == "__main__":
    args = read_config()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 try:
    sock.connect((args['host'], args['port']))

    serial = args['serial']
    user_access_level = args['user_access_level']
    passwd = args['passwd']

    mercury236.check_connect(sock, serial)
    mercury236.open_channel(sock, serial, user_access_level, passwd)

    # Получение и хранение данных
    result = {
        'vap': mercury236.read_vap(sock, serial),  # Напряжение, ток, мощность
        'energy': mercury236.read_energy(sock, serial),  # Общее чтение энергии
        'energy_sum_act_react': mercury236.read_energy_sum_act_react(sock, serial, args['array_number']),  # Сумма активной и реактивной энергии
        'energy_beginning_of_month': mercury236.read_energy_beginning_of_month(sock, serial),  # Энергия на начало месяца
        'freq': mercury236.read_freq(sock, serial),  # Частота сети
        'energy_sum_by_phases': mercury236.read_energy_sum_by_phases(sock, serial),  # Сумма энергии по фазам
        'energy_tarif_by_phase': mercury236.read_energy_tarif_by_phase(sock, serial)  # Энергия по тарифам и фазам
    }

    mercury236.close_channel(sock, serial)
except TimeoutError:
    result = {'error': "Timeout while reading data from socket"}
except ValueError:
    result = {'error': "Wrong data"}
except Exception as e:
    result = {'error': str(e)}
finally:
    sock.close()

print_output(result, args['format'])
