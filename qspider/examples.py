# -*- coding: utf-8 -*-
from .core import *

def test_of_thread():
    """Example of multi-threading"""
    import requests, random

    class ThreadTask(Task):
        def __init__(self, task_source):
            Task.__init__(self, task_source)
        
        def run(self):
            res = requests.get(self.task_source, timeout=5)
            if random.randint(0, 100) < 5:
                raise Exception()
            return res.status_code

    source = ['http://www.baidu.com' for i in range(500)]
    tm = ThreadManager(source, ThreadTask, has_result=True, add_failed=True)
    results = tm.run()
    print(len(results))

mp.freeze_support()

import random

class ProcessTask(Task):
    """Example of multi-processing"""
    def __init__(self, task_source):
        Task.__init__(self, task_source)
    
    def run(self):
        for i in range(1000000):
            continue
        if random.randint(0, 100) < 5:
            raise Exception()
        return self.task_source**2

def test_of_processing():
    source = list(range(500))
    pm = ProcessManager(source, ProcessTask, has_result=True, add_failed=True)
    results = pm.run()
    print(len(results))

if __name__=="__main__":
    test_of_thread()
    # test_of_processing()

