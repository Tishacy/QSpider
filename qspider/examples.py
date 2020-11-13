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

import random
import multiprocessing as mp
import logging
import requests

from .core import Task
from .core import ThreadManager
from .core import ProcessManager
from .decorators import concurrent

logging.basicConfig(level=logging.INFO)


# Class examples
def test_of_thread():
    """Example of multi-threading"""
    import requests

    class ThreadTask(Task):
        def __init__(self, task_source):
            Task.__init__(self, task_source)

        def run(self):
            res = requests.get(self.task_source, timeout=5)
            if random.randint(0, 100) < 5:
                raise Exception("Random exception")
            return res.status_code

    source = ['http://www.baidu.com' for _ in range(500)]
    tm = ThreadManager(source, ThreadTask, has_result=True, add_failed=True)
    results = tm.run(silent=False)
    print(len(results))


mp.freeze_support()


class ProcessTask(Task):
    """Example of multi-processing"""

    def __init__(self, task_source):
        Task.__init__(self, task_source)

    def run(self):
        for i in range(1000000):
            continue
        if random.randint(0, 100) < 5:
            raise Exception()
        return self.task_source ** 2


def test_of_processing():
    source = list(range(500))
    pm = ProcessManager(source, ProcessTask, has_result=True, add_failed=True)
    results = pm.run()
    print(len(results))


# Decorator examples
def get_source():
    return ['http://www.baidu.com' for _ in range(500)]


# Task class test
@concurrent.thread_class(get_source(), has_result=True, add_failed=True)
class MyTask(Task):
    def __init__(self, *args):
        Task.__init__(self, *args)

    def run(self):
        res = requests.get(self.task_source, timeout=5)
        logging.info(f"\rGET {self.task_source}, Response code: {res.status_code}")
        return res.status_code


# Task function test
@concurrent.thread_func(get_source(), has_result=True)
def my_task(task_source):
    res = requests.get(task_source, timeout=5)
    return res.status_code


if __name__ == "__main__":
    test_of_thread()
    test_of_processing()
    MyTask().run(silent=True)
    my_task(silent=False)
