# -*- coding: utf-8 -*-
import functools, inspect

from .core import ThreadManager, ProcessManager, Task

class concurrent(object):
    """Some concurrent decorators.
    """
    @staticmethod
    def thread_class(source, *args, **kwargs):
        """multi-threading task class decorator
        
        Attributes
            :param source: (iterable) the sources that tasks in the task 
                queue need for running tasks.
            :param task_cls: (subclass of Task or any class with a run method, 
                function, method) 
                task class to instantiate tasks or task function/ task method.
        """
        def decorator(task_cls):
            @functools.wraps(task_cls)
            def wrapper(*wargs, **wkwags):
                thread_manager = ThreadManager(source, task_cls, *args, **kwargs)
                return thread_manager
            return wrapper
        return decorator
    
    @staticmethod
    def thread_func(source, *args, **kwargs):
        """multi-threading task function decorator
        
        Attributes
            :param source: (iterable) the sources that tasks in the task 
                queue need for running tasks.
            :param task_cls: (subclass of Task or any class with a run method, 
                function, method) 
                task class to instantiate tasks or task function/ task method.
        """
        def decorator(task_cls):
            @functools.wraps(task_cls)
            def wrapper(*wargs, **wkwags):
                thread_manager = ThreadManager(source, task_cls, *args, **kwargs)
                return thread_manager.run()
            return wrapper
        return decorator
