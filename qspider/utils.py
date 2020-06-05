# -*- coding: utf-8 -*-
import os
import time
import datetime
from termcolor import colored

def display_progress(start_time, cur_size, tot_size, ncols=35, prog_char='█', desc=None):
    perc = cur_size / tot_size
    done = int(perc * ncols)
    desc_str = '%s ' %(desc) if desc else ''
    cur_time = time.time()
    rate = cur_size/(cur_time-start_time) if (cur_time != start_time) else 0
    left_time = (tot_size - cur_size) // rate if rate > 0 else 0
    left_time_str = str(datetime.timedelta(seconds=left_time))
    cost_time_str = '%.1f' %(time.time() - start_time)
    msg = '%s%3d%% |%s%s| %s/%s [eta-%s, %ss, %.1fit/s]' %(desc_str, perc*100, 
            prog_char*(done), ' '*(ncols-done), 
            cur_size, tot_size, 
            left_time_str, cost_time_str,
            rate)
    print(msg + '\b' * len(msg), end='', flush=True)
    if cur_size == tot_size:
        print()

def format_class_name(spider_name):
    return spider_name.capitalize() + 'Spider'

def get_resource_path(path):
    dir_path = os.path.dirname(__file__)
    dir_path = dir_path if dir_path else os.getcwd()
    return os.path.join(dir_path, path)

INFO = colored('[Info]', 'green')
INPUT = colored('[Input]', 'green')
WARN = colored('[Warn]', 'yellow')
ERROR = colored('[Error]', 'red')
PROGRESS_DESC_STRS = '←↖↑↗→↘↓↙'
PROGRESS_DESCS = [colored('[ %s ]' %(desc), 'yellow') for desc in PROGRESS_DESC_STRS]
DONE_DESC = colored('[ ✔ ]', 'green')
