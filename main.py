import os
import psutil
from datetime import datetime
import csv
import os.path
import time
import numpy as np
import pandas as pd
import sys
import daemonocle

import configuration as cfg


folder_path = os.path.dirname(os.path.abspath(__file__))
database_check = os.path.exists(f'{folder_path}/database.csv')
columns = ['name', 'pid', 'cpu_perc', 'memory_perc', 'io_rw_bytes', 'datetime']
called_PIDs = set()


# creates the database with a header if it does not exist
def create_database():
    if not database_check:
        with open(f'{folder_path}/database.csv', mode="w", newline='', encoding='utf-8') as database:
            csv_writer = csv.writer(database, quoting=csv.QUOTE_MINIMAL, delimiter=',')
            csv_writer.writerow(columns)


def collect_data_default():
    with open(f'{folder_path}/database.csv', mode="a", newline='', encoding='utf-8') as database:
        csv_writer = csv.writer(database, quoting=csv.QUOTE_MINIMAL, delimiter=',')

        while True:
            date_time = datetime.now()

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters']):
                p_name = proc.info['name']
                p_pid = proc.info['pid']
                # turning a default 0 from the first time a process is called
                # into nan value to skip them in later calculations
                if p_pid not in called_PIDs:
                    p_cpu_perc = np.nan
                    called_PIDs.add(p_pid)
                else:
                    p_cpu_perc = proc.info['cpu_percent']
                p_mem_perc = proc.info['memory_percent']
                p_io = proc.info['io_counters']
                if p_io is not None:
                    # calculating io usage as a total of
                    # read_bytes and write_bytes attributes
                    p_io_rw = p_io.read_bytes + p_io.write_bytes
                else:
                    p_io_rw = 0
                csv_writer.writerow([p_name, p_pid, p_cpu_perc, p_mem_perc, p_io_rw, date_time])

            # using sleep to prevent cases in which the script
            # would perform slower than the time period set in configuration
            time.sleep(cfg.main_X)


def collect_data_top_N(N):
    while True:
        date_time = datetime.now()

        with open(f'{folder_path}/current_batch.csv', mode="w", newline='', encoding='utf-8') as current_batch:
            current_batch_writer = csv.writer(current_batch, quoting=csv.QUOTE_MINIMAL, delimiter=',')

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters']):
                p_name = proc.info['name']
                p_pid = proc.info['pid']
                # turning default 0 from the first time a process is called
                # into nan value to skip them in later calculations
                if p_pid not in called_PIDs:
                    p_cpu_perc = np.nan
                    called_PIDs.add(p_pid)
                else:
                    p_cpu_perc = proc.info['cpu_percent']
                p_mem_perc = proc.info['memory_percent']
                p_io = proc.info['io_counters']
                if p_io is not None:
                    # calculating io usage as a total of
                    # read_bytes and write_bytes attributes
                    p_io_rw = p_io.read_bytes + p_io.write_bytes
                else:
                    p_io_rw = 0
                current_batch_writer.writerow([p_name, p_pid, p_cpu_perc, p_mem_perc, p_io_rw, date_time])

            current_batch_data = pd.read_csv(f'{folder_path}/current_batch.csv', names=columns)
            top_cpu = current_batch_data[['name', 'pid', 'cpu_perc', 'datetime']].nlargest(N, 'cpu_perc').reset_index(drop=True)
            top_memory = current_batch_data[['name', 'pid', 'memory_perc', 'datetime']].nlargest(N, 'memory_perc').reset_index(drop=True)
            top_io = current_batch_data[['name', 'pid', 'io_rw_bytes', 'datetime']].nlargest(N, 'io_rw_bytes').reset_index(drop=True)

            # only top values for a specific column collected,
            # remaining 2 columns as NaN to prevent multiple calculations
            # of the same entry in reports
            new_data = top_cpu.append([top_memory, top_io])
            rearanged_new_data = new_data[columns]
            rearanged_new_data.to_csv(f'{folder_path}/database.csv', mode='a', header=False, index=False, na_rep=np.nan)

        # using sleep to prevent cases in which the script
        # would perform slower than the time period set in configuration
        time.sleep(cfg.main_X)


def main():
    create_database()
    if cfg.main_N == 0:
        collect_data_default()
    else:
        collect_data_top_N(cfg.main_N)


if __name__ == '__main__':
    daemon = daemonocle.Daemon(worker=main, pid_file="/tmp/main.pid")
    try:
        daemon.do_action(sys.argv[1])
    except IndexError:
        print('Please run the script with one of the arguments:'
              'start/stop/restart/status, e.g. python3 main.py start')
