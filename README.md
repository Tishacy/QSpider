# QSpider

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT) [![Pyversion](https://img.shields.io/badge/python-3.x-green)](https://pypi.org/project/qspider/) [![Version](https://img.shields.io/badge/pypi-v0.1.5-red)](https://pypi.org/project/qspider)

An easy to use tools module for writing multi-thread and multi-process programs.

## Install

QSpider could be easily installed using pip:

```bash
$ pip install qspider
```

## Example

```python
import requests
from qspider import concurrent

# Define a source list for task function to parse.
def get_source():
    """Return a url list."""
    return ['http://www.baidu.com' for i in range(500)]

# Define the task function and add a thread_func decorator
# The thread_func decorator needs a source list, and other options (num_workers, has_result ...) as arguments
@concurrent.thread_func(source=get_source(), num_workers=100, has_result=True)
def my_task(task_source):
    """A customized task function.
    Process the task_source and return the processed results.

    Arguments
    :param task_source: the elem in the source list, which is a url here.
    :rtype: (int) A http status code.
    """
    url = task_source
    res = requests.get(url, timeout=5)
    return res.status_code

# Execute the task function.
results = my_task()
print(results)
```

Results of the example is as below:

```bash
[Info] 500 tasks in total.
[ ✔ ] 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 500/500 [eta-0:00:00, 0.9s, 542.9it/s]
[200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, ..., 200, 200, 200, 200]
```


## Releases

-   v0.1.1: First release with basic classes.
-   v0.1.2: Reconstruct code, add ThreadManager, ProcessManager and other tool classes.
-   v0.1.3: Fix multiprocess locking bug on Windows.
-   v0.1.4:
    - Add silent argument in manager._run method.
    - Enhance the display style of the progress message.
-   v0.1.5:
    - Make task be either a class, a function or a class method.
    - Add concurrent decorators for convenient use.
    - Add concurrent decorator examples.

## License

Copyright (c) 2020 tishacy.

Licensed under the [MIT License](https://github.com/Tishacy/QSpider/blob/master/LICENSE).