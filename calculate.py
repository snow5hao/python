# -*- encoding:utf-8 -*-
from urllib import request
import http.cookiejar
import re
import threading
import time
import pymysql
from queue import Queue
from bs4 import BeautifulSoup
# host="localhost"
# user="root"
# passwd="root"
host="172.168.1.161"
user="jack"
passwd="root1234"
a=[]
d=Queue(10000)
url="http://fund.eastmoney.com/233009.html?spm=search"

def getSoup(url,charset="utf-8",code="233009"):
    url = re.sub(r'[0-9]{6}', code, url)
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = request.HTTPCookieProcessor(cj)
    opener = request.build_opener(cookie_support, request.HTTPHandler)
    request.install_opener(opener)
    req = request.Request(url)
    req.add_header('User-agent',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36')
    req.add_header('Host', 'fund.eastmoney.com')
    req.add_header('Referer', 'http://fund.eastmoney.com/trade/hh.html')
    content = request.urlopen(req).read().decode(charset,'ignore')
    soup = BeautifulSoup(content, "html.parser")
    return soup

#返回今天之前的第5个交易日期

def caldate(code):
    soup=getSoup(url,'utf-8',code)  #poptableWrap poptableWraphb
    #print(code)
    jdate = soup.find_all("div", class_="poptableWrap singleStyleHeight01")
    #print(len(jdate))
    if len(jdate)==0:
        jdate = soup.find_all("div", class_="poptableWrap poptableWraphb")
    tdlist = jdate[0].table.find_all("td", class_="alignLeft")
    flag=1
    for i in tdlist:
        flag += 1
        if flag==6:
            return i.string
    if flag<=6:
        return 2
    #     foundInfo.put(a[flag])
    #     flag += 1
    # # 近5日涨幅
    # fiveDay = 0
    # flag = 0
    # for i in history:
    #     if (flag < 5):
    #         x = float(re.sub(r'%', "", str(i.span.string)))
    #         fiveDay += x
    #         flag += 1
    # foundInfo.put("5日跌幅：" + str(fiveDay) + "%")
#caldate("000009")
def calIncrease():
    global a
    db = pymysql.connect(host, user, passwd, "found", charset="utf8")
    cursor=db.cursor()
    sql="select code from foundabout;"
    cursor.execute(sql)
    for row in cursor.fetchall():
        sql = "select jztable from code_jinzhi where code='" + row[0] + "';"
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result[0][0])==0 and caldate(row[0])==2:
            continue
        s = time.strftime("%Y", time.localtime()) + "-" + caldate(row[0])
        sql="select jinzhi from "+ result[0][0] +" where code='"+row[0]+"' and jzdate>='"+s+"';"
        cursor.execute(sql)
        for ilte in cursor.fetchall():
            a.append(ilte[0])
        zf=(float(a[0])-float(a[-1]))/float(a[-1])
        zf=abs(round(zf,2))
        if a[0]<a[-1] and zf>=5:
            print("a[0]",a[0])
            print("a[1]",a[-1])
            print("zf",zf)
            print("就是它")
            print(row[0])
            exit(0)


        #     try:
        #         s = time.strftime("%Y", time.localtime()) + "-" + caldate(row[0])
        #         sql = "select jinzhi from hisjinzhi_100 where code='" + row[0] + "' and jzdate>=" + s
        #
        #     except:
        #         continue
        #
        # else:
        #     s=time.strftime("%Y",time.localtime())+"-"+caldate(row[0])
        #     sql="select jztable from code_jinzhi where code='"+row[0]+"';"
        #     cursor.execute(sql)
        #     result=cursor.fetchall()
        #     sql="select jinzhi from "+ result[0][0] +" where code='"+row[0]+"' and jzdate>='"+s+"';"
        #     cursor.execute(sql)
        #     for row in cursor.fetchall():

calIncrease()

