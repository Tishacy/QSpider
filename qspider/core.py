# -*- coding: utf-8 -*-
import time
import shutil
import threading as td
import multiprocessing as mp
import inspect
from queue import Queue
from abc import ABC, abstractmethod
from colorama import init

from .utils import *

init()
term_width, _ = shutil.get_terminal_size()

# Base classes
class SharedCounter:
    """A shared counter to among multiple threads or processes.
    This counter is a thread-safe counter if counter_type is 'thread',
    or a process-safe counter if counter_type is 'process'. 

    Attritbutes
        :param n: optional (int) the initial value of the counter.
        :param counter_type: optional (str) either to be 'thread' or 'process'
    """
    def __init__(self, n=0, counter_type='thread'):
        self.counter_type = counter_type
        self.count = n if self.counter_type == 'thread' else mp.Value('i', n)

    def increment(self, n=1):
        """Increment the counter by n (default = 1)."""
        if self.counter_type == 'thread':
            with td.Lock():
                self.count += n
        else:
            with self.count.get_lock():
                self.count.value += n

    @property
    def value(self):
        """Return the value of the counter."""
        if self.counter_type == 'thread':
            return self.count
        else:
            return self.count.value

class BaseQueue(ABC):
    """An abstract base queue based on multiple queue classes.
    This BaseQueue could be a FIFO/LIFO queue when passing different
    queue_cls arguments.
    BaseQueue is an abstract class, which means it must be inherited
    before it can be instantiated.

    Attributes
        :param counter_type: (str) either to be 'thread' or 'process'

        :param queue_cls: (Queue class or its subclass) based queue class
        
        :param lock_cls: (Lock class or its subclass) could be thread-lock
            or process-lock based on different needs.
        
        :param tasks: optional (iterable) the initial tasks, could be any
            iterable types. Elements the tasks should be instances of the
            subclass of Task class, which has a run method.
    """
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
        """Put a Task instance into the queue.
        :param task: (Task or its subclass) a Task instance
        """
        with self.lock:
            self.queue.put(task)
            self.qsize.increment(1)
    
    def get(self):
        """Get a Task instance out of the queue
        :rtype (Task or its subclass): 
        """
        task = None
        with self.lock:
            if self.qsize.value > 0:
                task = self.queue.get()
                self.qsize.increment(-1)
        return task

    def task_done(self):
        """Increase the num_task_done if task_done is called.
        This should be called every time the Task is done.
        """
        with self.lock:
            self.num_task_done.increment(1)
    
    def empty(self):
        """Return if the queue is empty.
        :rtype (bool): whether the queue is empty
        """
        return self.qsize.value == 0


class Task(ABC):
    """An abstract task class with a run method.
    Any class that inherits this class has to overwrite 
    the run method.
    Task is an abstract class, which means it must be inherited
    before it can be instantiated.

    Attributes
        :param task_source: (object) the source that the task needs when 
            then task run. task_source could be any type.
    """
    def __init__(self, task_source):
        self.task_source = task_source
    
    @abstractmethod
    def run(self):
        """Run method in a task"""

    def __str__(self):
        return "Task{source=%s}" %(str(self.task_source))

class BaseWorker(ABC):
    """An abstract worker class which implements a special Producer/Consumer
    model, which the instance could be a Thread or a Process instance. 
    Each worker gets a Task instance from the task queue, runs the task, and
    put the results of the task (if there are results returned by task) into the 
    results queue. 
    If there are exceptions exist when the worker run the task, the worker will
    put the task back into the task queue if failed_queue argument is None, else
    it will put the task into the failed queue.
    BaseWorker is an abstract class, which means it must be inherited
    before it can be instantiated.
    
    Attributes
        :param task_queue: (subclass of BaseQueue) task queue contains task instances.
        :param res_queue: optioanl (Queue or its subclass) results queue contains the results 
            returned by the task.run method.
        :param failed_queue: optional (subclass of BaseQueue) failed queue contains failed 
            task instances.
    """
    def __init__(self, task_queue, res_queue=None, failed_queue=None):
        self.task_queue = task_queue
        self.res_queue = res_queue
        self.failed_queue = failed_queue
    
    def _run(self):
        """Run tasks in the task queue until the queue is empty."""
        while True:
            task = self.task_queue.get()
            if not task:
                break
            try:
                if (type(task) == dict and 'caller' in task and 'source' in task):
                    res = task['caller'](task['source'])
                else:
                    res = task.run()
                if self.res_queue:
                    self.res_queue.put(res)
                self.task_queue.task_done()
            except Exception as e:
                if self.failed_queue:
                    self.failed_queue.put(task)
                    self.task_queue.task_done()
                    msg = "%s Task went wrong and added it into failed queue: %s" %(ERROR, task)
                    print("%s%s" %(msg, ' ' * (term_width - len(msg) + 3)))
                else:
                    self.task_queue.put(task)
                    msg = "%s Task went wrong and added it into task queue: %s" %(ERROR, task)
                    print("%s%s" %(msg, ' ' * (term_width - len(msg) + 3)))

class BaseManager(ABC):
    """An abstract manager class to manage all the queues and workers,
    which could be a multi-thread manager or a multi-process manager, 
    depending on the type of workers. 

    Attributes
        :param source: (iterable) the sources that tasks in the task 
            queue need for running tasks.

        :param task_cls: (subclass of Task or any class with a run method, 
            function, method) 
            task class to instantiate tasks or task function/ task method.

        :param worker_cls: (subclass of BaseWorker) worker class, which 
            could be the ThreadWorker or ProcessWorker class.

        :param task_queue_cls (subclass of TaskQueue): task queue class, 
            which could be the ThreadTaskQueue or ProcessTaskQueue class.

        :param res_queue_cls (Queue): (Queue or its subclass) results queue class.

        :param has_result: optional (bool) whether there are returned values from 
            the task.run method.
            Ther manager will instantiate the results queue if has_result is True, 
            otherwise the result queue is always None. Default is False.

        :param num_workers: optional (int or None) number of workers, could be None 
            or int values:
                None: input the number of workers in the command line.
                int: could be any positive integer. but when using ProcessWorker 
                    as worker_cls, the number of workers being equals to or less than 
                    the number of cpu cores is recommended.
            Default is None.

        :param add_failed: optional (bool) whether add failed tasks back into the
            task queue.
            True: Put the failed tasks back into the task queue.
            False: Put the failed tasks into the failed queue.
    """
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
        if inspect.isfunction(self.task_cls) or inspect.ismethod(self.task_cls):
            self.tasks = [{'caller': self.task_cls, 'source': src_item} for src_item in self.source]
        else:
            self.tasks = [self.task_cls(src_item) for src_item in self.source]
        self.task_queue = task_queue_cls(self.tasks)
        self.res_queue = res_queue_cls() if has_result else None
        self.failed_queue = task_queue_cls() if not add_failed else None
    
    def run(self, silent=False):
        """Run tasks in the task queue using multi-workers."""
        if not silent:
            msg = "%s %d tasks in total." %(INFO, len(self.tasks))
            print("%s%s" %(msg, ' ' * (term_width - len(msg) + 3)))
        self.num_workers = self.num_workers or self._get_num_workers()

        if not silent:
            timer = Timer(self.task_queue, fps=.1)
            timer.start()

        workers = []
        for i in range(self.num_workers):
            worker = self.worker_cls(self.task_queue, self.res_queue, self.failed_queue)
            worker.start()
            workers.append(worker)
        
        if not silent:
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

        results = []
        if self.has_result:
            while not self.res_queue.empty():
                results.append(self.res_queue.get())
        return results

    def crawl(self):
        """[Deprecated] Use run method instead"""
        return self.run()
    
    def test(self, index=0):
        """Test if the task.run method could run without any exceptions."""
        task = self.tasks[index]
        if type(task) == dict and 'caller' in task and 'source' in task:
            return task['caller'](task['source'])
        return task.run()

    def _get_num_workers(self):
        """Input the number of workers in the command line."""
        print(INPUT, end="")
        num_workers_str = input(" Number of workers: ")
        try:
            num_workers = int(num_workers_str)
            return num_workers
        except Exception as e:
            print('%s %s' %(WARN, e))
            return self._get_num_workers()

# Mult-threading 
class ThreadTaskQueue(BaseQueue):
    """A thread task queue contains tasks.

    Attributes
        :param tasks: optional (iterable) the initial tasks, could be any
            iterable types. Elements the tasks should be instances of the
            subclass of Task class, which has a run method."""
    def __init__(self, tasks=[]):
        BaseQueue.__init__(self, 'thread', Queue, td.Lock, tasks)
    
class ThreadWorker(Thread, BaseWorker):
    """A thread worker class which implements a special Producer/Consumer
    model, which the instance is a Thread instance. 
    Each worker gets a Task instance from the task queue, runs the task, and
    put the results of the task (if there are results returned by task) into the 
    results queue. 
    If there are exceptions exist when the worker run the task, the worker will
    put the task back into the task queue if failed_queue argument is None, else
    it will put the task into the failed queue.
    
    Attributes
        :param task_queue: optional (subclass of BaseQueue) task queue contains task instances.
        :param res_queue: optional (Queue or its subclass) results queue contains the results 
            returned by the task.run method.
        :param failed_queue: (subclass of BaseQueue) failed queue contains failed task instances.
    """
    def __init__(self, task_queue, res_queue=None, failed_queue=None):
        Thread.__init__(self)
        BaseWorker.__init__(self, task_queue, res_queue, failed_queue)

    def run(self):
        self._run()

class ThreadManager(BaseManager):
    """A multi-thread manager class to manage all the queues and workers.

    Attributes
        :param source: (iterable) the sources that tasks in the task 
            queue need for running tasks.

        :param task_cls: (subclass of Task or any class with a run method, 
            function, method) 
            task class to instantiate tasks or task function/ task method.

        :param has_result: optional (bool) whether there are returned values from 
            the task.run method.
            Ther manager will instantiate the results queue if has_result is True, 
            otherwise the result queue is always None. Default is False.

        :param num_workers: optional (int or None) number of workers, could be None or int values:
            None: input the number of workers in the command line.
            int: could be any positive integer. but when using ProcessWorker 
                as worker_cls, the number of workers being equals to or less than 
                the number of cpu cores is recommended.
            Default is None.

        :param add_failed: optional (bool) whether add failed tasks back into the
            task queue.
            True: Put the failed tasks back into the task queue.
            False: Put the failed tasks into the failed queue.
    """
    def __init__(self, source, task_cls, has_result=False, num_workers=None, add_failed=True):
        BaseManager.__init__(self, source, 
                             task_cls, 
                             ThreadWorker, 
                             ThreadTaskQueue, 
                             Queue,
                             has_result, 
                             num_workers,
                             add_failed)

class QSpider(ThreadManager):
    def __init__(self, source, task_cls, has_result=False, num_workers=None, add_failed=True):
        ThreadManager.__init__(self, source, task_cls, has_result, num_workers, add_failed)


# Multi-processing
class ProcessTaskQueue(BaseQueue):
    """A process task queue contains tasks.

    Attributes
        :param tasks: optional (iterable) the initial tasks, could be any
            iterable types. Elements the tasks should be instances of the
            subclass of Task class, which has a run method."""
    def __init__(self, tasks=[]):
        # BaseQueue.__init__(self, 'process', mp.Manager().Queue, mp.Lock, tasks)
        BaseQueue.__init__(self, 'process', mp.Manager().Queue, mp.Manager().Lock, tasks)

class ProcessWorker(mp.Process, BaseWorker):
    """A process worker class which implements a special Producer/Consumer
    model, which the instance is a Process instance. 
    Each worker gets a Task instance from the task queue, runs the task, and
    put the results of the task (if there are results returned by task) into the 
    results queue. 
    If there are exceptions exist when the worker run the task, the worker will
    put the task back into the task queue if failed_queue argument is None, else
    it will put the task into the failed queue.
    
    Attributes
        :param task_queue: (subclass of BaseQueue) task queue contains task instances.
        :param res_queue: optional (Queue or its subclass) results queue contains the results 
            returned by the task.run method.
        :param failed_queue: optional (subclass of BaseQueue) failed queue contains failed task instances.
    """
    def __init__(self, task_queue, res_queue=None, failed_queue=None):
        mp.Process.__init__(self)
        BaseWorker.__init__(self, task_queue, res_queue, failed_queue)

    def run(self):
        self._run()

class ProcessManager(BaseManager):
    """A multi-process manager class to manage all the queues and workers.

    Attributes
        :param source: (iterable) the sources that tasks in the task 
            queue need for running tasks.

        :param task_cls: (subclass of Task or any class with a run method, 
            function, method) 
            task class to instantiate tasks or task function/ task method.

        :param has_result: optional (bool) whether there are returned values from 
            the task.run method.
            Ther manager will instantiate the results queue if has_result is True, 
            otherwise the result queue is always None. Default is False.

        :param num_workers: optional (int or None) number of workers, could be None or int values:
            None: input the number of workers in the command line.
            int: could be any positive integer. but when using ProcessWorker 
                as worker_cls, the number of workers being equals to or less than 
                the number of cpu cores is recommended.
            Default is None.

        :param add_failed: optional (bool) whether add failed tasks back into the
            task queue.
            True: Put the failed tasks back into the task queue.
            False: Put the failed tasks into the failed queue.
    """
    def __init__(self, source, task_cls, has_result=False, num_workers=None, add_failed=True):
        BaseManager.__init__(self, source, 
                             task_cls, 
                             ProcessWorker, 
                             ProcessTaskQueue, 
                             mp.Manager().Queue,
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
    parser.add_argument('-p', '--process', action='store_true', help="Using multi-process instead of multi-thread template")
    args = parser.parse_args()

    spider_path = './{0}.py'.format(args.name)
    if os.path.isfile(spider_path):
        raise ValueError("File %s.py already exists, please change your spider name." %(args.name))

    template_fpath = get_resource_path('templates/process_template.py') if args.process else get_resource_path('templates/thread_template.py')
    templ_path = get_resource_path(template_fpath)
    class_name = format_class_name(args.name)
    templ = open(templ_path, 'r', encoding='utf-8').read().format(class_name, args.name)
    with open(spider_path, 'w', encoding='utf-8') as f:
        f.write(templ)
    print("A qspider named %s is initialized." %(args.name))

if __name__=="__main__":
    genqspider()
    