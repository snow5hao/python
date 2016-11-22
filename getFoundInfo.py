# -*- encoding:utf-8 -*-
from urllib import request
import http.cookiejar
import re
import threading
import time
import pymysql
import hashlib
from datetime import datetime
from queue import Queue
from bs4 import BeautifulSoup

now=datetime.now()
now.strftime('%Y-%m-%d %H:%M:%S')
foundInfo=Queue(10000)            #保存基金的总信息
foundCodeUrlQueue = Queue(500)  #保存含有基金代码的url地址列表
saveFoundCode = []   #保存所有的基金代码
threads = []
allFoundCode = Queue(10000)
host="172.168.1.161"
user="jack"
passwd="root1234"
jsq=0               #计数器
#插入时间
foundInfo.put("当前时间:"+now.strftime('%Y-%m-%d %H:%M:%S'))

#含有基金信息的url地址
foundAboutUrl="http://fund.eastmoney.com/f10/jbgk_233009.html"
foundDetailUrl="http://fund.eastmoney.com/233009.html?spm=search"
allFoundUrl="http://fund.eastmoney.com/daogou/#dt0;ft;rs;sd;ed;pr;cp;rt;tp;rk;se;nx;scz;stdesc;pi1;pn20;zfdiy;shlist"
foundUrl="http://fund.eastmoney.com/allfund.html"
hisJinZhiUrl="http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=233009&page=6&per=20&sdate=&edate=&rt=0.7782273583645574"




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
    s=["近一周","近一月","近3月","近6月","今年来","近1年","近2年","近3年"]
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

#获取所有的基金代码和基金名字，保存在数据库中,也可能通过再次执行来更新
def getAllCode():
    soup=getSoup(foundUrl,"gb2312")
    allf=soup.find_all("ul",class_="num_right")
    db = pymysql.connect(host, user, passwd, "found", charset="utf8")
    cursor = db.cursor()
    for i in allf:
        x=i.find_all(text=re.compile("[0-9]{6,}"))
        for allcode in x:
            codeNum=re.search("[0-9]{6,}",allcode)
            codeName=re.sub(r'\（[0-9]{6,}\）',"",allcode)
            sql = "select code from foundabout where code='"+codeNum.group(0)+"';"
            cursor.execute(sql)
            if len(cursor.fetchall())==0:
                sql=str("insert into foundabout values(null,'"+codeNum.group(0)+"','"+codeName+"');")
                cursor.execute(sql)
                db.commit()

#根据基金名字查询基金代码
def getFoundName():
    code=input("请输入你要查询的基金名字:")
    db = pymysql.connect(host, user, passwd, "found", charset="utf8")
    cursor = db.cursor()
    sql="select name,code from foundabout where name like '%"+code+"%';"
    cursor.execute(sql)
    for row in cursor.fetchall():
        print(row[1]+" : "+row[0])

#返回 int 总页数，
#参数code ,基金代码
def totalPage(code):
    soup=getSoup(hisJinZhiUrl,'utf-8',code)
    result=soup.find_all(text=re.compile("pages"))
    x=re.search('pages:.*\,',result[0])
    return int(re.sub(r'\D',"",x.group(0)))

#获取基金历史净值
#参数 code：基金代码，page，要获取的页
def getJinzhi(code,page):
    url="http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code="+code+"&page="+str(page)+"&per=20&sdate=&edate=&rt=0.7782273583645574"
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = request.HTTPCookieProcessor(cj)
    opener = request.build_opener(cookie_support, request.HTTPHandler)
    request.install_opener(opener)
    req = request.Request(url)
    req.add_header('User-agent',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36')
    req.add_header('Host', 'fund.eastmoney.com')
    req.add_header('Referer', 'http://fund.eastmoney.com/f10/jjjz_080015.html')
    content = request.urlopen(req).read().decode('utf-8', 'ignore')
    soup = BeautifulSoup(content, "html.parser")
    db = pymysql.connect(host, user,passwd, "found", charset="utf8")
    cursor = db.cursor()
    #查出基金净值应该存储在的表
    sql="select jztable from code_jinzhi where code='"+code+"';"
    cursor.execute(sql)
    result=cursor.fetchall()
    flag=0
    for i in soup.find_all("tr"):
        if flag!=0:
            #跳过查找到的第一个tr
            jz=i.find("td","tor bold").string
            jzdate=i.find_all(text=re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}"))
            if len(result) == 0:
                sql = "insert into hisjinzhi_100 values(null,'" + code + "','" + jzdate[0] + "','" + jz + "');"
            else:
                sql = "insert into " + result[0][0] + " values(null,'" + code + "','" + jzdate[0] + "','" + jz + "');"
            cursor.execute(sql)
            db.commit()
            #检查数据库中时候存在某个日期的净值数据,如果存在就终止函数执行，返回1，
    #         sql="select jinzhi from "+result[0][0]+" where jzdate='"+jzdate[0]+"';"
    #         cursor.execute(sql)
    #         if len(cursor.fetchall())==0:
    #             sql="insert into "+result[0][0]+" values(null,'"+code+"','"+jzdate[0]+"','"+jz+"');"
    #             cursor.execute(sql)
    #             db.commit()
    #         else:
    #             return 1
    # return 2
        flag += 1


#获取数据库中所有基金的历史所有净值
def getAllJinZhi():
    while not allFoundCode.empty():
        code=allFoundCode.get()
        totalpage = totalPage(code)
        if totalpage==0:
            continue
        page = 1
        while page <= totalpage:
            getJinzhi(code, page)
            page += 1

#检查输入的基金代码是否正确
#参数：n ，可以输入的次数
def checkInputCode(n):
    global jsq
    global code
    n -= 1
    code = input("请输入你要查询的基金代码:")
    db = pymysql.connect(host, user, passwd, "found", charset="utf8")
    cursor = db.cursor()
    cursor.execute("select * from foundabout");
    result = cursor.fetchall()
    for row in result:
        saveFoundCode.append(row[1])
    if (str(re.match('^[0-9]{6}$', code))=="None"):
        print("您输入的基金代码有误，请重新输入")
        jsq+=1
        if n < 1 :
            print("你会不会啊，输了"+str(jsq)+"次还输不对")
            exit(1)
        else:
            checkInputCode(n)
    elif code not in saveFoundCode:
        print("你找基金在数据库中不存在，可以尝试更新数据库")
        exit(1)
    return code

#创建多线程
class myThread(threading.Thread):
    def __init__(self,threadName):
        threading.Thread.__init__(self)
        self.threadName=threadName
    def run(self):
        print(self.threadName+" started……")
        getAllJinZhi()
        print(self.threadName+"ending……")

#开启多线程
def openMutiThread():
    threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4","Thread-5", "Thread-6", "Thread-7", "Thread-8","Thread-9", "Thread-10"]
    for iname in threadList:
        thread = myThread(iname)
        thread.start()
        threads.append(thread)


#++++++++++++++++++++主程序开始++++++++++++++++++++++++
print("-------------欢迎来到基金优选程序：---------------")
flag=0
while flag==0:
    promot="=====================\n" \
           "请输入您要选择的功能:\n" \
           "1：查询基金代码\n" \
           "2：查询基金基本信息\n" \
           "3：更新数据库的基金代码\n" \
           "4: 更新基金历史净值\n" \
           "5：退出\n" \
           "=====================\n"
    choice=input(promot)
    if choice=="1":
        getFoundName()
    if choice=="2":
        code = checkInputCode(3)
        try:
            getFoundInfo(code)
        except:
            print("找不到相关信息，可能该基金还未开放认购")
        while not foundInfo.empty():
            print(foundInfo.get())
    if choice=="3":
        try:
            getAllCode()
        except:
            print("更新发生错误")
    if choice=="4":
        try:
            db = pymysql.connect(host, user, passwd, "found", charset="utf8")
            cursor = db.cursor()
            sql = "select code from foundabout;"
            cursor.execute(sql)
            for row in cursor.fetchall():
                allFoundCode.put(row[0])
            openMutiThread()
            for i in threads:
                i.join()
            print(time.ctime())
            print("Exiting main threading")
        except:
            print("更新历史净值发生错误咯，你个大傻逼")
    if choice=="5":
        flag=1






