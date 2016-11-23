import re
from urllib import parse, request, error
import http.cookiejar
from PIL import Image
import time
import json
import urllib
email_url = 'https://www.zhihu.com/login/email'
phone_url = 'http://www.zhihu.com/login/phone_num'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:48.0) Gecko/20100101 Firefox/48.0'}
cj = http.cookiejar.LWPCookieJar()
cookie_support = urllib.request.HTTPCookieProcessor(cj)
opener = urllib.request.build_opener(cookie_support, request.HTTPHandler)

# 给openner添加headers, addheaders方法接受元组而非字典
opener.addheaders = [(key, value) for key, value in headers.items()]
request.install_opener(opener)

def get_xsrf():
    """
    获取参数_xsrf
    """
    req = opener.open('https://www.zhihu.com')
    html = req.read().decode('utf-8')
    get_xsrf_pattern = re.compile(r'<input type="hidden" name="_xsrf" value="(.*?)"')
    _xsrf = re.findall(get_xsrf_pattern, html)[0]
    return _xsrf


def get_captcha():
    """
    获取验证码本地显示
    返回你输入的验证码
    """
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r='+t+"&type=login"
    print(t)
    request.urlretrieve(captcha_url, 'cptcha.gif')
    # image_data = request.urlopen(captcha_url).read()
    # with open('cptcha.gif', 'wb') as f:
    #     f.write(image_data)
    im = Image.open('cptcha.gif')
    im.show()
    captcha = input('本次登录需要输入验证码： ')
    return captcha


def login(username, password):
    """
    输入自己的账号密码，模拟登录知乎
    """
    # 检测到11位数字则是手机登录
    if re.match(r'\d{11}$', account):
        print('使用手机登录中...')
        url = phone_url
        data = {'_xsrf': get_xsrf(),
                'password': password,
                'remember_me': 'true',
                'phone_num': username
                }
    else:
        print('使用邮箱登录中...')
        url = email_url
        data = {'_xsrf': get_xsrf(),
                'password': password,
                'remember_me': 'true',
                'email': username
                }
    # 若不用验证码，直接登录

    try:
        data['captcha'] = get_captcha()
        post_data = parse.urlencode(data).encode('utf-8')
        r = opener.open(url, post_data)
        result = r.read().decode('utf-8')
        print((json.loads(result))['msg'])
        # print(get_xsrf)
    except:
        pass
    # 保存cookie到本地

if __name__ == '__main__':
    account = input('输入账号：')
    secret = input('输入密码：')
    login(account, secret)

    # 设置里面的简介页面，登录后才能查看。以此来验证确实登录成功
    get_url = 'https://www.zhihu.com/settings/profile'
    try:
        get = opener.open(get_url)
        content = get.read().decode('utf-8')
        print(content)
    except error.HTTPError as e:
        print(e.reason)
    except error.URLError as e:
        print(e.reason)