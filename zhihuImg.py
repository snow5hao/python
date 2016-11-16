#-*- coding:utf-8 -*-
from urllib import request
from urllib import parse
import re
from bs4 import BeautifulSoup
import http.cookiejar
import urllib
url='https://www.zhihu.com/'
urlfirst='https://www.zhihu.com/people/xu-xiang-jie-25'
posturl='http://www.zhihu.com/login/phone_num'
hosturl='http://www.zhihu.com/#signin'

proxysp=request.ProxyHandler({'http':'http://203.91.121.74:3128'})
opener=request.build_opener(proxysp,request.HTTPHandler)

request.install_opener(opener)
cj = http.cookiejar.LWPCookieJar()
cookie_support = urllib.request.HTTPCookieProcessor(cj)
opener = urllib.request.build_opener(cookie_support, request.HTTPHandler)
request.install_opener(opener)
def getImg():
    req=request.Request(urlfirst,headers={'User-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'})
    data=request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(data,"html.parser")
    pre=soup.find_all("img",class_="Avatar Avatar--l")
    for i in pre:
        print(i.attrs['src'])
#getImg()
def get_xsrf():
    """
    获取参数_xsrf
    """
    req = opener.open('https://www.zhihu.com')
    html = req.read().decode('utf-8')
    get_xsrf_pattern = re.compile(r'<input type="hidden" name="_xsrf" value="(.*?)"')
      # 这里会返回多个值，不过都是一样的内容，取第一个就行
    _xsrf = re.findall(get_xsrf_pattern, html)[0]
    return _xsrf
def loginzh():
    urllib.request.install_opener(opener)
    xsrf=get_xsrf()
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    postData = parse.urlencode([
        ('_xsrf', xsrf),
        ('phone_num', '18750929449'),
        ('remember_me', 'true'),
        ('password', 'ssrs_95zz')
    ])
    request = urllib.request.Request(posturl, postData.encode('utf-8'), headers)
    text = urllib.request.urlopen(request).read()
    print(text.decode('utf-8'))
loginzh()
