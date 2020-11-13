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

from .core import QSpider
from .core import Task
from .core import ThreadManager
from .core import ThreadTaskQueue
from .core import ThreadWorker
from .core import ProcessManager
from .core import ProcessTaskQueue
from .core import ProcessWorker
from .core import SharedCounter
from .core import genqspider

from .utils import INFO
from .utils import INPUT
from .utils import WARN
from .utils import ERROR
from .utils import Timer
from .utils import display_progress

from .decorators import concurrent


__all__ = ['QSpider', 'ThreadManager', 'ThreadTaskQueue', 'ThreadWorker', 'Task',
           'ProcessManager', 'ProcessTaskQueue', 'ProcessWorker', 'genqspider',
           'SharedCounter', 'display_progress', 'Timer', 'INFO', 'WARN', 'ERROR', 'INPUT',
           'concurrent']
