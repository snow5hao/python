# -*- encoding:utf-8 -*-
import threading
from urllib import request
from queue import Queue
import re
import time
print(time.ctime())
s=set()
q=Queue(100)
exitFlag=0
url='http://172.168.1.161/zblog'
data = request.urlopen(url).read().decode('utf-8')
patt = re.compile(r'href=\"(http:\/\/172.168.1.161\/zblog\/\?id=\d{1,3})')
urllist = re.findall(patt, data)
for i in urllist:
    if i not in s:
        q.put(i)
        s.add(i)
print(len(s))
class myThread(threading.Thread):
    def __init__(self,threadName,q):
        threading.Thread.__init__(self)
        self.threadName=threadName
        self.q=q
    def run(self):
        #print(self.threadName+" started....")
        #print("q size", q.qsize())
        #working(self.threadName,self.q)
        finurl()
        #print(self.threadName+" exit")
def getUrl(url):
    data = request.urlopen(url).read().decode('utf-8')
    patt = re.compile(r'href=\"(http:\/\/172.168.1.161\/zblog\/\?id=\d{1,3})')
    urllist = re.findall(patt, data)
    for i in urllist:
        if i not in s:
            q.put(i)
            s.add(i)

def finurl():
    i=q.get()
    getUrl(i)
    if len(s)>150:
        return
    finurl()
def working(threadName,q):
    while not exitFlag:
        if not q.empty():
            urlone=q.get()
            getUrl(urlone)
            print("process "+threadName)

threads=[]
threadList=["Thread-1","Thread-2","Thread-3","Thread-4"]
for iname in threadList:
    thread=myThread(iname,q)
    thread.start()
    threads.append(thread)

while not q.empty():
    pass
exitFlag=1
for i in threads:
    i.join()
for i in s:
    print("end:"+i)
print(len(s))
print("Exit main thread")
print(time.ctime())