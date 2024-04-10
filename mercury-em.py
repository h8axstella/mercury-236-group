import configparser
import socket
import json
import os
import mercury.mercury236 as mercury236

def read_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def save_results_to_file(data, results_dir, file_name='results.json'):
    os.makedirs(results_dir, exist_ok=True)  # Создаем папку, если она еще не существует
    file_path = os.path.join(results_dir, file_name)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def print_output(arr, output_format):
    if output_format == "json":
        print(json.dumps(arr, indent=4))

def poll_meter(host, port, serial, user, passwd, user_access_level):
    result = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        mercury236.check_connect(sock, serial)
        mercury236.open_channel(sock, serial, user, passwd, user_access_level)

        result = {
            'vap': mercury236.read_vap(sock, serial),
            'energy': mercury236.read_energy(sock, serial),
            'energy_sum_act_react': mercury236.read_energy_sum_act_react(sock, serial),
            'energy_beginning_of_month': mercury236.read_energy_beginning_of_month(sock, serial),
            'freq': mercury236.read_freq(sock, serial),
            'energy_sum_by_phases': mercury236.read_energy_sum_by_phases(sock, serial),
            'energy_tarif_by_phase': mercury236.read_energy_tarif_by_phase(sock, serial)
        }

        mercury236.close_channel(sock, serial)
    except Exception as e:
        result = {'error': str(e)}
    finally:
        sock.close()
    
    return result

if __name__ == "__main__":
    config = read_config()
    user = config.get('General', 'user')
    passwd = config.get('General', 'passwd')
    user_access_level = config.getint('General', 'user_access_level')
    output_format = config.get('General', 'format', fallback='json')
    results_dir = config.get('General', 'results_dir', fallback='results')  # Читаем из конфига

    all_results = []  # Список для хранения результатов всех опросов

    for section in config.sections():
        if 'Transformer' in section:
            host = config.get(section, 'host')
            port = config.getint(section, 'port')
            meters = config.get(section, 'meters').split(', ')
            for serial in meters:
                result = poll_meter(host, port, serial, user, passwd, user_access_level)
                all_results.append(result)
    
    if output_format == 'json':
        save_results_to_file(all_results, results_dir)
