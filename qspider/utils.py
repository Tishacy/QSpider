# MIT License
#
# Copyright (c) 2020 tishacy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import time
import datetime
import itertools
import shutil
import logging
from termcolor import colored
from threading import Thread

logging.basicConfig(level=logging.INFO)

if os.name == 'nt':
    from colorama import init
    init()


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
        [ ✔ ] 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100/100 [eta-0:00:00, 0.1s, 1000it/s]
        
    """
    ncols = ncols or shutil.get_terminal_size()[0]
    # unprog_char = ' ' if os.name == 'nt' else prog_char
    unprog_char = prog_char

    perc = cur_size / tot_size
    desc_str = '%s ' % desc if desc else ''
    cur_time = time.time()
    rate = cur_size/(cur_time-start_time) if (cur_time != start_time) else 0
    left_time = (tot_size - cur_size) // rate if rate > 0 else 0
    left_time_str = str(datetime.timedelta(seconds=left_time))
    cost_time_str = '%.1f' % (time.time() - start_time)

    # format progress msg
    status_column = desc_str
    percentage_column = colored('%3d%%' % (perc * 100), 'blue')
    ratio_column = colored('%s/%s' % (cur_size, tot_size), "blue")
    time_column = '[eta-%s, %ss, %sit/s] ' % (
        colored(left_time_str, "yellow"),
        colored(cost_time_str, "yellow"),
        colored("%.1f" % rate, "yellow")
    )
    bar_len = ncols - len(status_column + percentage_column + ratio_column + time_column) + 9 * 5
    bar_column = '%s%s' % (
        colored(prog_char * int(perc * bar_len), 'green'),
        colored(unprog_char * int(bar_len - perc * bar_len), 'white')
    )
    msg = f"{status_column} {percentage_column} {bar_column} {ratio_column} {time_column}"

    print('\r' + msg, end='', flush=True)
    if cur_size == tot_size:
        print()


def format_class_name(spider_name):
    """Format the spider name to A class name."""
    return spider_name.capitalize() + 'Spider'


def get_resource_path(path):
    """Get the absolute path of a given file path."""
    dir_path = os.path.dirname(__file__)
    dir_path = dir_path if dir_path else os.getcwd()
    return os.path.join(dir_path, path)


INFO = colored('[Info]', 'green')
ERROR = colored('[Error]', 'red')
WARN = colored('[Warn]', 'yellow')
INPUT = colored('[Input]', 'green')
PROGRESS_DESC_STRS = '←↖↑↗→↘↓↙'
PROGRESS_DESCS = [
    colored('[ %s ]', 'blue') % desc for desc in PROGRESS_DESC_STRS
]
DONE_DESC = colored('[ ✔ ]', "blue")


class Timer(Thread):
    """A Timer thread class to display the progress of the accomplishment
    of tasks in the task queue.
    
    Attributes
        :param task_queue: (subclass of BaseQueue) task queue contains task instances.
        :param fps: optional (float) refresh rate. Default value is 0.1s.
    """
    def __init__(self, task_queue, fps=0.1, ncols=None):
        Thread.__init__(self)
        self.task_queue = task_queue
        self.tot_size = task_queue.tot_size.value
        self.fps = fps
        self.ncols = ncols

    def run(self):
        """Run the timer"""
        start_time = time.time()
        for desc in itertools.cycle(PROGRESS_DESCS):
            cur_size = self.task_queue.num_task_done.value
            desc = desc if cur_size < self.tot_size else DONE_DESC
            # prog_char = '#' if os.name == 'nt' else '━'  # ━ █
            prog_char = '━'  # ━ █
            display_progress(start_time, cur_size, self.tot_size, ncols=self.ncols, prog_char=prog_char, desc=desc)
            if cur_size == self.tot_size:
                break
            time.sleep(self.fps)
