
import logging 

logging.basicConfig(level=logging.DEBUG)

logging.getLogger('octopus').setLevel(level=logging.DEBUG)
logging.getLogger('jaeger_tracing').setLevel(level=logging.ERROR)

import time
import random
import os 

os.environ['OCTOPUS_DIRECT_OMISSIONS'] = 'listen'
os.environ['OCTOPUS_DIRECT_OMISSIONS

from Octopus.tracing import octopus

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
    
    def listen(self):
        
        for i in range(5):
            
            test.bar_foo()

            test.foo_bar()
    

test = TestChild()

octopus.profiled_instance(test)

test.listen()