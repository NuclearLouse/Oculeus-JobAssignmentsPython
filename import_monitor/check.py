#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import sys
import time
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
    

def write_alert(number_files, folder, config):
    alert_time = time.strftime("%H:%M:%S", time.localtime())
    time_for_name = time.strftime("%y%m%d", time.localtime())
    path_alert_file = config.get('DEFAULT', 'pathalertfile')
    alert_file = path_alert_file + 'parser_' + time_for_name + '.error.log'
    source_folder = config.get(folder, 'path')
    message = config.get(folder, 'alertmessage')
    alert_message = '000030' + '|' + alert_time + '|' + 'WARNING' + '|' + message + \
        ' folder '+ source_folder + ' contains ' + number_files + ' of unprocessed files'
    #print(alert_message) # визуальная проверка, потом убрать
    alert_files = open(alert_file, 'a')
    alert_files.write(alert_message + '\n')
    alert_files.close()

def write_state_ini(path, section, key, value, state):
    state.set(section, key, value)
    f = open(path, 'w')
    state.write(f)
    f.close()

def folder_scanner():
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_path, 'check.ini')
    state_file = os.path.join(base_path, 'state.ini')
    
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
    else:
        print("Config not found! Exiting!")
        sys.exit(1)

    if os.path.exists(state_file):
        state = configparser.ConfigParser()
        state.read(state_file)
    else:
        #print("State file not found! Create new file.") # визуальная проверка, потом убрать
        state = configparser.ConfigParser()
        for section in config.sections():
            state.add_section(section)
            state.set(section, 'status', '0')
            state.set(section, 'lastflagtime', '0')
            state.set(section, 'maxnumfiles', '0')
        f = open(state_file, 'w')
        state.write(f)
        f.close()

    for folder in config.sections():
        source_path = config.get(folder, 'Path')
        file_type = config.get(folder, 'FileExtension')
        max_num_files = int(state.get(folder, 'maxnumfiles'))
        files_number = len(glob.glob(source_path + file_type))
        if files_number > max_num_files:
            write_state_ini(state_file, folder, 'maxnumfiles', str(files_number), state)
        if files_number >= int(config.get(folder, 'FilesNumber')):
            alert_time = time.mktime(time.localtime())
            if state.get(folder, 'status') == '1':
                last_time = state.get(folder, 'lastflagtime')
                delta = alert_time - float(last_time)
                if delta >= float(config.get(folder, 'checkinterval'))*60:
                    write_state_ini(state_file, folder, 'lastflagtime', str(alert_time), state)
                    write_alert(str(files_number), folder, config)
            else:
                write_state_ini(state_file, folder, 'status', '1', state)
                write_state_ini(state_file, folder, 'lastflagtime', str(alert_time), state)

        else:
            write_state_ini(state_file, folder, 'status', '0', state)

if __name__ == "__main__":
    folder_scanner()




