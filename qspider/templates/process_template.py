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

from qspider import ProcessManager
from qspider import Task

class {0}(ProcessManager):
    def __init__(self, has_result=False, add_failed=True):
        self.name = "{1}"
        self.has_result = has_result
        self.add_failed = add_failed
        self.source = [0]
        super({0}, self).__init__(self.source, self.task, has_result=self.has_result, add_failed=self.add_failed)

    def task(self, task_source):
        # parse single task source
        pass

if __name__=="__main__":
    qspider = {0}()
    qspider.test()
    # qspider.run()
