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

import functools

from .core import ThreadManager


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
            def wrapper():
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
            def wrapper(*wargs, **wkwargs):
                thread_manager = ThreadManager(source, task_cls, *args, **kwargs)
                return thread_manager.run(*wargs, **wkwargs)
            return wrapper
        return decorator
