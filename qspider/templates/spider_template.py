# -*- coding: utf-8 -*-

from qspider.core import QSpider, Task

class {0}(QSpider):
    def __init__(self, has_result=False, add_failed=True):
        self.name = "{1}"
        self.has_result = has_result
        self.add_failed = add_failed
        self.source = [0]
        super({0}, self).__init__(self.source, self.QTask, has_result=self.has_result, add_failed=self.add_failed)

    class QTask(Task):
        def __init__(self, task_source):
            Task.__init__(self, task_source)
            
        def run(self):
            # parse single task source
            pass

if __name__=="__main__":
    qspider = {0}()
    qspider.test()
    # qspider.crawl()
