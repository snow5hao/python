# -*- encoding:utf-8 -*-
from urllib import request
import http.cookiejar
import re
import threading
import time
import pymysql
from datetime import datetime
from queue import Queue
from bs4 import BeautifulSoup

now=datetime.now()
now.strftime('%Y-%m-%d %H:%M:%S')
foundInfo=Queue(10000)            #保存基金的总信息
foundCodeUrlQueue = Queue(500)  #保存含有基金代码的url地址列表
saveFoundCode = Queue(100000)   #保存所有的基金代码

jsq=0               #计数器
#插入时间
foundInfo.put("当前时间:"+now.strftime('%Y-%m-%d %H:%M:%S'))

#含有基金信息的url地址
foundAboutUrl="http://fund.eastmoney.com/f10/jbgk_233009.html"
foundDetailUrl="http://fund.eastmoney.com/233009.html?spm=search"
allFoundUrl="http://fund.eastmoney.com/daogou/#dt0;ft;rs;sd;ed;pr;cp;rt;tp;rk;se;nx;scz;stdesc;pi1;pn20;zfdiy;shlist"
foundUrl="http://fund.eastmoney.com/allfund.html"

#返回url的soup
# 参数：包含基金信息url,基金代码code（默认是查询摩尔因子）
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


#获取基金的涨幅等信息,把结果保存在foundInfo列队中
#参数：code 基金代码,默认是233009
def getFoundInfo(code="233009"):
    soup = getSoup(foundDetailUrl,'utf-8',code)
    #查找基金名字
    jname=soup.find_all("div",class_="fundDetail-tit")
    for i in jname:
        foundInfo.put("您要查找的基金是："+i.text)
    #查找出估算净值和单位净值
    jinzhi = soup.find_all("dd", class_="dataNums")
    gs=jinzhi[0].find("dl",class_="floatleft")
    foundInfo.put("估算净值:"+gs.span.string)
    foundInfo.put("单位净值:"+jinzhi[1].span.string)
    #估算涨幅
    zhangfu=soup.find_all(id="gz_gszzl")
    zhangfu[0].string
    #插入估算涨幅
    foundInfo.put("实时估算涨幅:"+zhangfu[0].string)
    #插入历史涨幅
    foundInfo.put("历史涨幅：")
    #涨幅时间
    a = []
    jdate=soup.find_all("div",class_="poptableWrap singleStyleHeight01")
    tdlist=jdate[0].table.find_all("td",class_="alignLeft")
    for i in tdlist:
        a.append(i.string)
    #历史涨幅
    flag=0
    history=soup.find_all("td",class_="RelatedInfo alignRight10 bold")
    for i in history:
        a[flag]=a[flag]+" : "+i.span.string
        foundInfo.put(a[flag])
        flag += 1
    #近5日涨幅
    fiveDay=0
    flag=0
    for i in history:
        if(flag<5):
            x=float(re.sub(r'%',"",str(i.span.string)))
            fiveDay+=x
            flag+=1
    foundInfo.put("5日跌幅："+str(fiveDay)+"%")
    #历史长时间的涨幅
    longtime=soup.find(id="increaseAmount_stage")
    x=longtime.find_all(text=re.compile("%"))
    s=set(["一周","一月","近3月","近6月","今年来","近1年","近2年","近3年"])
    flag=0
    for i in s:
        zfstr=i+" : "+x[flag]
        flag+=1
        foundInfo.put(zfstr)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#获取含有基金代码列表的所有url地址
#暂时这个函数不用
def FoundCodeUrl():
    soup = getSoup(allFoundUrl)
    # 获取总的页数
    x = soup.find_all(id="pager_lite")
    allPageNum = x[0].find_all(text=re.compile("^\/[0-9]{3}"))
    allPageNum = re.sub(r'\D', "", allPageNum[0])

    # 获取包含基金代码的url列表，保存在foundCodeUrlQueue里面
    for i in range(int(allPageNum)):
        foundCodeUrl = "http://fund.eastmoney.com/daogou/#dt0;ft;rs;sd;ed;pr;cp;rt;tp;rk;se;nx;scz;stdesc;pi" + str(i + 1) + ";pn20;zfdiy;shlist"
        foundCodeUrlQueue.put(foundCodeUrl)

#获取所有的基金代码，保存在saveFoundCode中
#暂时这个函数不能用
def getFoundCode(threadName):
    #用来保存所有的基金代码
    while not foundCodeUrlQueue.empty():
        # 获取每页含有的基金代码
        url=foundCodeUrlQueue.get()
        soup=getSoup(url)
        fondList = soup.find_all(id="fund_list")
        x = fondList[0].find_all(text=re.compile("[0-9]{6}"))
        for i in x :
            saveFoundCode.put(i)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#获取所有的基金代码和基金名字，保存在数据库中和saveFoundCode列队中
def getAllCode():
    soup=getSoup(foundUrl,"gb2312")
    #allf=soup.find_all(text=re.compile("[0-9]{6,}"))
    allf=soup.find_all("ul",class_="num_right")
    db = pymysql.connect("localhost","root","root","found",charset="utf8" )
    cursor=db.cursor()
    for i in allf:
        x=i.find_all(text=re.compile("[0-9]{6,}"))
        for allcode in x:
            codeNum=re.search("[0-9]{6,}",allcode)
            codeName=re.sub(r'\（[0-9]{6,}\）',"",allcode)
            sql=str("insert into foundabout values(null,'"+codeNum.group(0)+"','"+codeName+"');")
            cursor.execute(sql)
            saveFoundCode.put(codeNum.group(0))
        db.commit()
        #获取基金名字

code=0
#检查输入的基金代码是否正确
#参数：n ，可以输入的次数
def checkInputCode(n):
    global jsq
    global code
    n -= 1
    code = input("请输入你要查询的基金代码:")
    if (str(re.match('^[0-9]{6}$', code))=="None"):
        print("您输入的基金代码有误，请重新输入")
        jsq+=1
        if n < 1 :
            print("你会不会啊，输了"+str(jsq)+"次还输不对")
            exit(1)
        else:
            checkInputCode(n)
    elif code not in saveFoundCode:
        print("你找的是火星上的基金吗？反正我是没找到这只鸡")
        exit(1)
    return code

#创建多线程
class myThread(threading.Thread):
    def __init__(self,threadName):
        threading.Thread.__init__(self)
        self.threadName=threadName
    def run(self):
        print(self.threadName+" started……")
        getFoundCode(self.threadName)
        print(self.threadName+"ending……")

#主程序+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

code=checkInputCode(3)
getFoundInfo(code)
while not foundInfo.empty():
    print(foundInfo.get())

# while not foundCodeUrlQueue.empty():
#     print(foundCodeUrlQueue.get())
# exit(0)
threads=[]
threadList=["Thread-1","Thread-2","Thread-3","Thread-4"]
for iname in threadList:
    thread=myThread(iname)
    #thread.start()
    threads.append(thread)

for i in threads:
    i.join()
print(time.ctime())
print("Exiting main threading")



