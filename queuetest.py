#encoding=utf-8

import queue
import threading
import time

exitFlag=0

threadList = ["Thread-1", "Thread-2", "Thread-3"]
nameList = ["One", "Two", "Three", "Four", "Five"]
queueLock = threading.Lock()
workQueue = queue.Queue(10)
threads = []
threadID = 1
class myThread(threading.Thread):
    def __init__(self,threadID,name,q):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.q=q
    def run(self):
        print('Starting '+self.name)
        process_data(self.name,self.q)
        print('Exiting '+self.name)
def process_data(threadName,q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data=q.get() 
            queueLock.release()
            print("%s processing %s" % (threadName,data))
        else:
            queueLock.release()
        time.sleep(1)

#创建并开始三个线程
for tname in threadList:
    thread=myThread(threadID,tname,workQueue)
    thread.start()
    threads.append(thread)
    threadID+=1

#填充列队   
queueLock.acquire()
for work in nameList:
    workQueue.put(work)
queueLock.release()

while not workQueue.empty():
    pass

exitFlag=1
for t in threads:
    t.join()
print("Exiting Main Thread")
















