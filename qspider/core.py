# -*- coding: utf-8 -*-
import time
from queue import Queue
from threading import Lock, Thread
from abc import ABC, abstractmethod
import itertools

from .utils import *

class TaskQueue:
    """Task Queue class
    """
    def __init__(self, tasks=[]):
        self.queue = Queue()
        self.lock = Lock()
        self.qsize = 0
        for task in tasks:
            self.add(task)
        self.tot_size = self.qsize

    def add(self, task):
        """Add task into task queue
        
        :param task: Task instance that be added into task queue.
        :rtype: None
        """
        self.lock.acquire()
        self.queue.put(task)
        self.qsize += 1
        self.lock.release()

    def get(self):
        """Get the first task out of task queue.
        
        :rtype: Task
        """

        task = None
        self.lock.acquire()
        if self.qsize > 0:
            task = self.queue.get()
            self.qsize -= 1
        self.lock.release()
        return task
    
    def task_done(self):
        """Indicate that a formerly enqueued task is complete."""
        return self.queue.task_done()
    

class Task(ABC):
    def __init__(self, task_source):
        self.task_source = task_source
    
    @abstractmethod
    def run(self):
        """Run method in a task"""

    def __str__(self):
        return "Task{source=%s}" %(str(self.task_source))


class Worker(Thread):
    """Worker"""
    def __init__(self, task_queue, res_queue=None):
        Thread.__init__(self)
        self.task_queue = task_queue
        self.res_queue = res_queue
    
    def run(self):
        while True:
            task = self.task_queue.get()
            if not task:
                break

            try:
                res = task.run()
                self.task_queue.task_done()
                
                if self.res_queue:
                    self.res_queue.put(res)
            except Exception as e:
                self.task_queue.add(task)
                print("[ ⚠✗ ] Task went wrong and added it into task queue: %s" %(task))

class Timer(Thread):
    def __init__(self, tot_size, res_queue, fps=0.1):
        Thread.__init__(self)
        self.tot_size = tot_size
        self.res_queue = res_queue
        self.fps = fps

    def run(self):
        start_time = time.time()
        for desc in itertools.cycle('←↖↑↗→↘↓↙'):
            cur_size = self.res_queue.qsize()
            desc = desc if cur_size < self.tot_size else '✔️'
            display_progress(start_time, cur_size, self.tot_size, prog_char='●', desc='[ %s ]' %desc)
            if (cur_size == self.tot_size):
                break
            time.sleep(self.fps)

class QSpider:
    def __init__(self, source, 
                 task_cls, 
                 has_result=False, 
                 num_threads=None):
    
        self.source = source
        self.task_cls = task_cls
        self.has_result = has_result
        self.num_threads = num_threads

        self.tasks = [self.task_cls(src_item) for src_item in self.source]
        self.task_queue = TaskQueue(self.tasks)
        self.res_queue = Queue() if has_result else None
        print("[Info] QSpider is ready.")

    def crawl(self):
        print("[Info] %d tasks in total." %(len(self.tasks)))
        self.num_threads = self.num_threads or self._get_num_threads()

        timer = Timer(self.task_queue.tot_size, self.res_queue, fps=.1)
        timer.start()

        workers = []
        for i in range(self.num_threads):
            worker = Worker(self.task_queue, self.res_queue)
            worker.start()
            workers.append(worker)
        
        timer.join()
        for worker in workers:
            worker.join()

        results = []
        if self.has_result:
            while not self.res_queue.empty():
                results.append(self.res_queue.get())
        return results
    
    def test(self, index=0):
        return self.tasks[index].run()

    def _get_num_threads(self):
        num_threads_str = input("[Input] Number of threads: ")
        return int(num_threads_str)



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

