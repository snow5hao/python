#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
from time import ctime
import time

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print("Starting " + self.name)
        threadLock.acquire()
        print_time(self.name, 3, self.counter)
        threadLock.release()

def print_time(threadName, delay, counter):
    while counter:
        time.sleep(delay)
        print("%s: %s" % (threadName, ctime()))
        counter -= 1

threadLock = threading.Lock()
threads = []

thread1 = myThread(1, "Thread-1", 2)
thread2 = myThread(2, "Thread-2", 3)

threads.append(thread1)
threads.append(thread2)

for t in threads:
    t.start()
t.join()
print("Exiting Main Thread")