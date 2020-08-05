# -*- coding: utf-8 -*-
import os
import time
import datetime
import itertools
import shutil
from colored import fg, bg, attr
from threading import Thread

def display_progress(start_time, cur_size, tot_size, ncols=None, prog_char='━', desc=None):
    """Display progress bar of current progress.

    :param start_time: (float) start time
    :param cur_size: (int) current progress.
    :param tot_size: (int) total size the tasks.
    :param ncols: optional (int) width of progress message, including bar column and other columns,
        such as status column, time column, etc. 
        Default value is None, which uses the width of the terminal.
    :param prog_char: optional (char) progress character. Default is '━'.
    :param desc: optional (str or None) string displayed in front of the progress bar.

    Example:
        >>> display_progress(time.time(), 100, 100, desc='[ ✔ ]')
        >>> [ ✔ ] 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100/100 [eta-0:00:00, 0.1s, 1000it/s]
        
    """
    ncols = ncols or shutil.get_terminal_size()[0]
    unprog_char = ' ' if os.name == 'nt' else prog_char

    perc = cur_size / tot_size
    desc_str = '%s ' %(desc) if desc else ''
    cur_time = time.time()
    rate = cur_size/(cur_time-start_time) if (cur_time != start_time) else 0
    left_time = (tot_size - cur_size) // rate if rate > 0 else 0
    left_time_str = str(datetime.timedelta(seconds=left_time))
    cost_time_str = '%.1f' %(time.time() - start_time)

    # formate progress msg
    status_column = desc_str
    percentage_column = '%s%3d%%%s ' %(fg('blue'), perc*100, attr('reset'))
    ratio_column = '%s%s/%s%s ' %(fg('light_magenta'), cur_size, tot_size, attr('reset')) 
    time_column = '[eta-%s, %ss, %sit/s] ' %(
        '%s%s%s' %(fg('yellow'), left_time_str, attr('reset')), 
        '%s%s%s' %(fg('yellow'), cost_time_str, attr('reset')), 
        '%s%.1f%s' %(fg('yellow'), rate, attr('reset')),
    )
    bar_len = ncols - len(status_column + percentage_column + ratio_column + time_column) + 14 * 5
    bar_column = '%s%s ' %(
        '%s%s%s' %(fg('green'), prog_char, attr('reset')) * int(perc * bar_len), 
        '%s%s%s' %(fg(242), unprog_char, attr('reset')) * int(bar_len - perc * bar_len), 
    )
    msg = status_column + percentage_column + bar_column + ratio_column + time_column

    print(msg + '\b' * len(msg), end='', flush=True)
    if cur_size == tot_size:
        print()

def format_class_name(spider_name):
    """Formate the spider name to A class name."""
    return spider_name.capitalize() + 'Spider'

def get_resource_path(path):
    """Get the absolute path of a given file path."""
    dir_path = os.path.dirname(__file__)
    dir_path = dir_path if dir_path else os.getcwd()
    return os.path.join(dir_path, path)


INFO = '%s[Info]%s' %(fg('green'), attr('reset'))
INPUT = '%s[Input]%s' %(fg('green'), attr('reset'))
WARN = '%s[Warn]%s' %(fg('yellow'), attr('reset'))
ERROR = '%s[Error]%s' %(fg('red'), attr('reset'))
PROGRESS_DESC_STRS = '←↖↑↗→↘↓↙'
PROGRESS_DESCS = [
    '%s[ %s ]%s' %(fg('blue'), desc, attr('reset'))
     for desc in PROGRESS_DESC_STRS
]
DONE_DESC = '%s[ ✔ ]%s' %(fg('blue'), attr('reset'))


class Timer(Thread):
    """A Timer thread class to display the progress of the accomplishment
    of tasks in the task queue.
    
    Attributes
        :param task_queue: (subclass of BaseQueue) task queue contains task instances.
        :param fps: optional (float) refresh rate. Default value is 0.1s.
    """
    def __init__(self, task_queue, fps=0.1):
        Thread.__init__(self)
        self.task_queue = task_queue
        self.tot_size = task_queue.tot_size.value
        self.fps = fps

    def run(self):
        """Run the timer"""
        start_time = time.time()
        for desc in itertools.cycle(PROGRESS_DESCS):
            cur_size = self.task_queue.num_task_done.value
            desc = desc if cur_size < self.tot_size else DONE_DESC
            prog_char = '#' if os.name == 'nt' else '━' # ━ █
            display_progress(start_time, cur_size, self.tot_size, prog_char=prog_char, desc=desc)
            if (cur_size == self.tot_size):
                break
            time.sleep(self.fps)

