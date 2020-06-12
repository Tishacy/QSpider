# -*- coding: utf-8 -*-
import time
import threading as td
import multiprocessing as mp
from queue import Queue
from abc import ABC, abstractmethod
from colorama import init

from .utils import *

init()

# Base classes
class SharedCounter:
    def __init__(self, n=0, counter_type='thread'):
        self.counter_type = counter_type
        self.count = n if self.counter_type == 'thread' else mp.Value('i', n)

    def increment(self, n=1):
        """ Increment the counter by n (default = 1) """
        if self.counter_type == 'thread':
            self.count += n
        else:
            with self.count.get_lock():
                self.count.value += n

    @property
    def value(self):
        """ Return the value of the counter """
        if self.counter_type == 'thread':
            return self.count
        else:
            return self.count.value

class BaseQueue(ABC):
    def __init__(self, counter_type, queue_cls, lock_cls, tasks=[]):
        self.counter_type = counter_type
        self.queue = queue_cls()
        self.lock = lock_cls()
        self.qsize = SharedCounter(0, self.counter_type)
        for task_source in tasks:
            self.put(task_source)
        self.num_task_done = SharedCounter(0, self.counter_type)
        self.tot_size = self.qsize
    
    def put(self, task):
        with self.lock:
            self.queue.put(task)
            self.qsize.increment(1)
    
    def get(self):
        task = None
        with self.lock:
            if self.qsize.value > 0:
                task = self.queue.get()
                self.qsize.increment(-1)
        return task

    def task_done(self):
        with self.lock:
            self.num_task_done.increment(1)
    
    def empty(self):
        return self.qsize.value == 0


class Task(ABC):
    def __init__(self, task_source):
        self.task_source = task_source
    
    @abstractmethod
    def run(self):
        """Run method in a task"""

    def __str__(self):
        return "Task{source=%s}" %(str(self.task_source))

class BaseWorker(ABC):
    def __init__(self, task_queue, res_queue=None, failed_queue=None):
        self.task_queue = task_queue
        self.res_queue = res_queue
        self.failed_queue = failed_queue
    
    def _run(self):
        while True:
            task = self.task_queue.get()
            if not task:
                break
            try:
                res = task.run()
                if self.res_queue:
                    self.res_queue.put(res)
                self.task_queue.task_done()
            except Exception as e:
                if self.failed_queue:
                    self.failed_queue.put(task)
                    self.task_queue.task_done()
                    print("%s Task went wrong and added it into failed queue: %s  " %(ERROR, task))
                else:
                    self.task_queue.put(task)
                    print("%s Task went wrong and added it into task queue: %s  " %(ERROR, task))

class BaseManager(ABC):
    def __init__(self, source,
                 task_cls,
                 worker_cls,
                 task_queue_cls,
                 res_queue_cls,
                 has_result=False,
                 num_workers=None,
                 add_failed=True):
        
        self.source = source
        self.task_cls = task_cls
        self.worker_cls = worker_cls
        self.task_queue_cls = task_queue_cls
        self.res_queue_cls = res_queue_cls
        self.has_result = has_result
        self.num_workers = num_workers

        self.tasks = [self.task_cls(src_item) for src_item in self.source]
        self.task_queue = task_queue_cls(self.tasks)
        self.res_queue = res_queue_cls() if has_result else None
        self.failed_queue = task_queue_cls() if not add_failed else None
    
    def run(self):
        print("%s %d tasks in total." %(INFO, len(self.tasks)))
        self.num_workers = self.num_workers or self._get_num_workers()

        timer = Timer(self.task_queue, fps=.1)
        timer.start()

        workers = []
        for i in range(self.num_workers):
            worker = self.worker_cls(self.task_queue, self.res_queue, self.failed_queue)
            worker.start()
            workers.append(worker)
        
        timer.join()
        for worker in workers:
            worker.join()

        if self.failed_queue and self.failed_queue.qsize.value > 0:
            flag = input("%s %d tasks failed, re-run failed tasks? (y/n): " %(WARN, self.failed_queue.qsize.value))
            if flag in ['y', 'Y']:
                self.task_queue = self.failed_queue
                self.task_queue.tot_size = self.task_queue.qsize
                self.num_workers = self._get_num_workers()
                self.failed_queue = self.task_queue_cls()
                return self.run()

        print(self.res_queue)
        results = []
        if self.has_result:
            while not self.res_queue.empty():
                results.append(self.res_queue.get())
        return results

    def crawl(self):
        """[Deprecated] Use run method instead"""
        return self.run()
    
    def test(self, index=0):
        return self.tasks[index].run()

    def _get_num_workers(self):
        print(INPUT, end="")
        num_workers_str = input(" Number of workers: ")
        return int(num_workers_str)


# Mult-threading 
class ThreadTaskQueue(BaseQueue):
    def __init__(self, tasks=[]):
        BaseQueue.__init__(self, 'thread', Queue, td.Lock, tasks)
    
class ThreadWorker(Thread, BaseWorker):
    def __init__(self, task_queue, res_queue=None, failed_queue=None):
        Thread.__init__(self)
        BaseWorker.__init__(self, task_queue, res_queue, failed_queue)

    def run(self):
        self._run()

class ThreadManager(BaseManager):
    def __init__(self, source, task_cls, has_result=False, num_workers=None, add_failed=True):
        BaseManager.__init__(self, source, 
                             task_cls, 
                             ThreadWorker, 
                             ThreadTaskQueue, 
                             Queue,
                             has_result, 
                             num_workers,
                             add_failed)

# Multi-processing
class ProcessTaskQueue(BaseQueue):
    def __init__(self, tasks=[]):
        BaseQueue.__init__(self, 'process', mp.JoinableQueue, mp.Lock, tasks)

class ProcessWorker(mp.Process, BaseWorker):
    def __init__(self, task_queue, res_queue=None, failed_queue=None):
        mp.Process.__init__(self)
        BaseWorker.__init__(self, task_queue, res_queue, failed_queue)

    def run(self):
        self._run()

class ProcessManager(BaseManager):
    def __init__(self, source, task_cls, has_result=False, num_workers=None, add_failed=True):
        BaseManager.__init__(self, source, 
                             task_cls, 
                             ProcessWorker, 
                             ProcessTaskQueue, 
                             mp.JoinableQueue,
                             has_result, 
                             num_workers,
                             add_failed)


# Command line tool
import argparse, os

def genqspider():
    """Generate your qspider based on templates.
    """
    parser = argparse.ArgumentParser("Generate your qspider based on templates")
    parser.add_argument('name', help="Your spider name")
    args = parser.parse_args()

    spider_path = './{0}.py'.format(args.name)
    if os.path.isfile(spider_path):
        raise ValueError("File %s.py already exists, please change your spider name." %(args.name))

    templ_path = get_resource_path('templates/spider_template.py')
    class_name = format_class_name(args.name)
    templ = open(templ_path, 'r', encoding='utf-8').read().format(class_name, args.name)
    with open(spider_path, 'w', encoding='utf-8') as f:
        f.write(templ)
    print("A qspider named %s is initialized." %(args.name))

if __name__=="__main__":
    genqspider()
    