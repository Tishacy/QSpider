# -*- coding: utf-8 -*-

from qspider import ProcessManager, Task

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
