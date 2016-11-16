# -*- encoding:utf-8 -*-
from urllib import request
import http.cookiejar
from bs4 import BeautifulSoup
url='http://fund.eastmoney.com/trade/pg.html?spm=001.1.swh#6y;desc'

cj = http.cookiejar.LWPCookieJar()
cookie_support = request.HTTPCookieProcessor(cj)
opener = request.build_opener(cookie_support, request.HTTPHandler)
request.install_opener(opener)
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:48.0) Gecko/20100101 Firefox/48.0'}
req=request.Request(url)
req.add_header('User-agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36')
req.add_header('Host','fund.eastmoney.com')
req.add_header('Referer','http://fund.eastmoney.com/trade/hh.html')
content=request.urlopen(req).read().decode('gb2312')
soup=BeautifulSoup(content,"html.parser")
