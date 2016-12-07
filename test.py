# -*- encoding:utf-8 -*-
import pymysql
import sys
from queue import Queue
from time import sleep
import time
# i=0
# while i<5:
#     i+=1
#     db = pymysql.connect("172.168.1.161", "jack", "root1234", "found", charset="utf8")
#     cursor = db.cursor()
#     sql2="select code from foundabout where id" \
#          "=000001;"
#     cursor.execute(sql2);
#     result = cursor.fetchall()
#     if len(result)==0:
#         print("空")
a=0
while a<3:
    b=0
    print("a"+str(a))
    while b<4:
        print("b"+str(b))
        if b==2:
            break
        b+=1
    a+=1