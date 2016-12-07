
import re
import pymysql
from urllib import request
import http.cookiejar
from bs4 import BeautifulSoup
#这个文件只是用来获取开放式基金里面的混合基金的代码
host="172.168.1.161"
user="jack"
passwd="root1234"
s=set()
openurl="http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=hh&rs=&gs=0&sc=zzf&st=desc&sd=2015-11-25&ed=2016-11-25&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1&v=0.9098432420732465"
openurl2="http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=zq&rs=&gs=0&sc=zzf&st=desc&sd=2015-11-25&ed=2016-11-25&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1&v=0.9098432420732465"
def getSoup(page,charset="utf-8"):
    #url="http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=hh&rs=&gs=0&sc=zzf&st=desc&sd=2015-11-25&ed=2016-11-25&qdii=&tabSubtype=,,,,,&pi="+str(page)+"&pn=50&dx=1&v=0.9098432420732465"
    url = "http://fund.eastmoney.com/api/FundGuide.aspx?dt=0&sd=&ed=&rt=sz,5_zs,5_ja,5&sc=rt_ja&st=desc&pi=1&pn=20&zf=diy&sh=list&rnd=0.2861980610304462"
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = request.HTTPCookieProcessor(cj)
    opener = request.build_opener(cookie_support, request.HTTPHandler)
    request.install_opener(opener)
    req = request.Request(url)
    req.add_header('User-agent',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36')
    req.add_header('Host', 'fund.eastmoney.com')
    req.add_header('Referer', 'http://fund.eastmoney.com/daogou/')
    content = request.urlopen(req).read().decode(charset,'ignore')
    soup = BeautifulSoup(content, "html.parser")
    return soup


def begMain(page):
    soup=getSoup(page)
    result=soup.find_all(text=re.compile("[0-9]{6}"))

    result=re.findall('\"[0-9]{6}\,',result[0])
    for i in result:
        result=re.sub(r'\D',"",i)
        s.add(result)

# for page in range(5):
#     t=page+1
#     begMain(t)
begMain(1)
for i in s:
    db = pymysql.connect(host, user, passwd, "found", charset="utf8")
    cursor = db.cursor()
    sql="insert into goodFounds values(null,'"+i+"','5',null);"
    cursor.execute(sql)
    db.commit()