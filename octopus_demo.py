
import time
import random
import os 

from Octopus.tracing import octopus

os.environ['JAEGER_HOST'] = 'localhost'
os.environ['JAEGER_PORT'] = '6831'
os.environ['SERVICE_NAME'] = 'test'

class Test:
    def foo(self):
        time.sleep(random.randint(1, 3))
        return 'bar'
    
    def bar(self):
        time.sleep(random.randint(1, 2))
        return 'foo'
    
    @staticmethod
    def foo_bar():
        time.sleep(random.randint(0, 10))
        return 'bar-foo'
    

class TestChild(Test):
    def bar_foo(self):
        time.sleep(random.randint(0, 3))
        
        self.foo()
        
        self.foo_bar()
        
        return 'bar_foo'
    

test = octopus.profiled_instance(TestChild())

for i in range(5):

    test.bar_foo()

    test.foo_bar()