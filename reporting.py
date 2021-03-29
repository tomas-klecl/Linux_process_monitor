import pandas as pd
import numpy as np

import configuration as cfg


stats = ['mean', 'max', 'median', 'perc_95']
attributes = ['cpu_perc', 'memory_perc', 'io_rw_bytes']


def perc_95(x):
    return x.quantile(0.95)


def create_reports():
    data = pd.read_csv('database.csv')
    # filter by the list of processes from the configuration
    if len(cfg.process_list) > 0:
        data = data[data['name'].isin(cfg.process_list)]
    # filter by the time period from the configuration
    if cfg.reporting_from:
        data = data[data['datetime'] > cfg.reporting_from]
    if cfg.reporting_to:
        data = data[data['datetime'] < cfg.reporting_to]

    # using only names and datetime for grouping as there are processes
    # with the same name but different PID (e.g. python3)
    # that I would like to aggregate
    data_sum = data.groupby(['name', 'datetime']).sum(min_count=1)  # to prevent nan values turning into 0
    report1 = data_sum.groupby(['name']).agg({'cpu_perc': ['count', 'mean', 'max', 'median', perc_95],
                                              'memory_perc': ['count', 'mean', 'max', 'median', perc_95],
                                              'io_rw_bytes': ['count', 'mean', 'max', 'median', perc_95]})
    report1.to_csv('report1.csv')

    report1.reset_index(inplace=True)
    # getting a separate dataframe for each stat and attribute
    # to concat them afterwards
    top_dataframes = []
    for atr in attributes:
        for stat in stats:
            top_df = report1[[('name', ''), (atr, 'count'), (atr, stat)]].nlargest(cfg.report2_N, (atr, stat)).reset_index(drop=True)
            top_dataframes.append(top_df)
    report2 = pd.concat(top_dataframes, axis=1)
    # matching index with the top position rank of a certain process
    report2.index = report2.index + 1
    report2.to_csv('report2.csv')


if __name__ == '__main__':
    create_reports()
