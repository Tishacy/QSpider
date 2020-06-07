# Spider

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT) [![Pyversion](https://img.shields.io/badge/python-3.x-green)](https://pypi.org/project/qspider/) [![Version](https://img.shields.io/badge/pypi-v0.1.1-red)](https://pypi.org/project/qspider)

Blocking queue crawler module for writing multi-threaded crawlers easily.

## Install

QSpider could be easily installed using pip:

```bash
$ pip install qspider
```

## Usages

### Using Module

```python
# 1. import class QSpider and Task from qspider.core module 
#   and other modules.
from qspider.core import QSpider, Task
import requests

# 2. Define a list of task source.
#   Each of the element in this source list is called 'task_source'.
#   'task_source' could be any type, ie str, tuple, object, dict...,
#   it could also be requests.Session or something else.
source = ['https://www.baidu.com' for i in range(100)]

# 3. Create your own task (which need to extends Task).
class TestTask(Task):
    """A test task
    
    Attributes:
        task_source: the source which needed in the task.
          which is actually the 'task_source' in the source list.
    """
    def __init__(self, task_source):
        Task.__init__(self, task_source)
    
    def run(self):
        # process the self.task_source here.
        res = requests.get(self.task_source, timeout=3)
        # return values needed
        return res.status_code
      
# 4. Create the QSpider and run it.
test_spider = QSpider(source, TestTask, has_result=True)
results = test_spider.crawl()
print(results)
```

Run the script and you'll get:

```bash
[Info] 100 tasks in total.
[Input] Number of threads: 20
[ ✔ ] 100% |███████████████████████████████████| 100/100 [eta-0:00:00, 2.5s, 40.8it/s]
[200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, ... , 200]
```

### Using command line

Create a QSpider using command:

```bash
$ genqspider -h
usage: Generate your qspider based on templates [-h] name

positional arguments:
  name        Your spider name

optional arguments:
  -h, --help  show this help message and exit
```

#### Example

1.  Create a `test` crawler using QSpider.

    ```bash
    $ genqspider test
    A qspider named test is initialized.
    ```

    A python script named `test.py` is created in your current directory.

2. Open the `test.py`，And you'll get:

    ```python
    # -*- coding: utf-8 -*-
    
    from qspider.core import QSpider, Task
    
    class TestSpider(QSpider):
        def __init__(self, has_result=False, add_failed=True):
            self.name = "test"
            self.has_result = has_result
            self.add_failed = add_failed
            self.source = [0]  # define your source list
            super(TestSpider, self).__init__(self.source, self.QTask, has_result=self.has_result, add_failed=self.add_failed)
    
        class QTask(Task):
            def __init__(self, task_source):
                Task.__init__(self, task_source)
                
            def run(self):
                # parse single task source
                pass
    
    if __name__=="__main__":
        qspider = TestSpider()
        qspider.test()
        # qspider.crawl()
    ```

3. Modify your source list with the line `self.source = [0]`, and how you gonna process the `task_source` in the method `QTask.run` .

    ```python
    # -*- coding: utf-8 -*-
    import requests
    from qspider.core import QSpider, Task
    
    class TestSpider(QSpider):
        def __init__(self, has_result=False, add_failed=True):
            self.name = "test"
            self.has_result = has_result
            self.add_failed = add_failed
            # 1. define your source list
            self.source = ['https://www.baidu.com' for i in range(100)]  
            super(TestSpider, self).__init__(self.source, self.QTask, has_result=self.has_result, add_failed=self.add_failed)
    
        class QTask(Task):
            def __init__(self, task_source):
                Task.__init__(self, task_source)
                
            # 2. Modify the run method
            def run(self):
                # process the self.task_source here.
                res = requests.get(self.task_source, timeout=3)
                # return values needed
                return res.status_code
    
    if __name__=="__main__":
      	# 3. 'has_result' is True when there are values returned in QTask.run method.
        qspider = TestSpider(has_result=True)
        # 4. receive the results after run the qspider.
        results = qspider.crawl()
        print(results)
    ```

4. Run the script and you'll get:

    ```bash
    [Info] 100 tasks in total.
    [Input] Number of threads: 20
    [ ✔ ] 100% |███████████████████████████████████| 100/100 [eta-0:00:00, 2.5s, 40.8it/s]
    [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, ... , 200]
    ```

## Releases

-   v0.1.0: First release with basic classes.

## License

Copyright (c) 2020 tishacy.

Licensed under the [MIT License](https://github.com/Tishacy/QSpider/blob/master/LICENSE).