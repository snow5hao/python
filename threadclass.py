#encoding=utf-8
import threading
from time import ctime,sleep
import time
exitFlag=0
class myThread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.counter=counter
    def run(self):
        print("starting"+self.name)
        print_time(self.name,self.counter,5)
        print("Exiting"+self.name)
     
def print_time(threadName,counter,delay):  
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print("%s:%s " % (threadName,ctime()))      
        counter-=1
thread1=myThread(1,"thread-1",2)
thread2=myThread(2,"thread-2",3)

#thread1.start()
#thread2.start()
threads=[]
threads.append(thread1)
threads.append(thread2)
for t in threads:
    t.start()
t.join()
print("Exiting Main Thread")