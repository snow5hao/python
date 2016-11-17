# -*- encoding:utf-8 -*-
from urllib import request
import http.cookiejar
import re
from datetime import datetime
from queue import Queue
from bs4 import BeautifulSoup

now=datetime.now()
now.strftime('%Y-%m-%d %H:%M:%S')
foundInfo=Queue(100)
#插入时间
foundInfo.put("当前时间:"+now.strftime('%Y-%m-%d %H:%M:%S'))

foundAboutUrl="http://fund.eastmoney.com/f10/jbgk_233009.html"
foundDetailUrl="http://fund.eastmoney.com/233009.html?spm=search"

#获取url的soup
def getSoup(code,url):
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
    content = request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(content, "html.parser")
    return soup



#code=input("请输入你要查询的基金代码:")
soup=getSoup("233009",foundDetailUrl)
#soup=getSoup("233009")
jinzhi=soup.find_all("span",class_="ui-font-large ui-color-red ui-num")

#查找基金名字
jname=soup.find_all("div",class_="fundDetail-tit")
for i in jname:
    foundInfo.put("您要查找的基金是："+i.text)

#查找出估算净值和单位净值
foundInfo.put("估算净值:"+jinzhi[0].string)
foundInfo.put("单位净值:"+jinzhi[1].string)

#估算涨幅
zhangfu=soup.find_all(id="gz_gszzl")
zhangfu[0].string
#插入估算涨幅
foundInfo.put("实时估算涨幅:"+zhangfu[0].string)

#插入历史涨幅
foundInfo.put("历史涨幅：")
a=[]
#涨幅时间
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
fiveDay="0"
flag="0"
for i in history:
    if(flag!=5):
        x=re.sub(r'%',"",str(i.span.string))
        fiveDay+=x
        #flag+=1
foundInfo.put("5日跌幅："+fiveDay)

#历史长时间的涨幅
longtime=soup.find(id="increaseAmount_stage")
x=longtime.find_all(text=re.compile("%"))
s=set(["一周","一月","近3月","近6月","今年来","近1年","近2年","近3年"])
flag=0
for i in s:
    str=i+" : "+x[flag]
    flag+=1
    foundInfo.put(str)

while not foundInfo.empty():
    print(foundInfo.get())
