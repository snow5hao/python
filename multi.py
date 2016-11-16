# -*- encoding:utf-8 -*-
import threading
from time import ctime ,sleep

def music(arg):
    for i in range(2):
        print("I want to listen to music %s, at %s" % (arg,ctime()))
        sleep(2)

def movie(arg):
    for i in range(2):
        print("Let us to see a movie %s, at %s" % (arg,ctime()))
        sleep(5)
   
threads=[] 
t1=threading.Thread(target=music,args=(u'爱情买卖',))
threads.append(t1)
t2=threading.Thread(target=movie,args=(u'卧虎藏龙',))
threads.append(t2)

if __name__ =='__main__':
    for t in threads:
        t.setDaemon(True)
        t.start()
        print(t.getName())
    t.join()
    print("all over at %s" % ctime())
