# -*- coding: utf-8 -*-
from json import loads as json_loads
from re import search as re_search
from time import sleep, strftime, localtime

from _ColorfulPyPrint import *
from cookies_convert import selenium2requests

try:
    from selenium import webdriver
except:
    errprint('需要selenium包的支持,请安装: pip install selenium')
try:
    from requests import session, Response as reqResponse, get
except:
    errprint('requests,请安装: pip install requests')

__version__ = '0.7.3'


def is_complied():
    from os.path import exists, dirname
    from os import sep

    try:
        if exists(dirname(__file__) + sep + '..' + sep + 'ShuoshuoMonitor.exe'):
            return True
        else:
            return False
    except:
        return False


def usage(error_code=0):
    global __version__
    import sys
    from os.path import basename
    if is_complied():
        program_exec_cmd = 'ShuoshuoMonitor'
    else:
        program_exec_cmd = 'python ' + basename(__file__)
    print('说说监控及秒赞工具 Version: %s' % __version__)
    print('### 本程序需要系统已安装firefox ###')
    print('    -h --help: 显示本帮助')
    print('    -s (selfQQ) --self-login: 指定自己的QQ并手动在浏览器中登陆')
    print('    -p (password) --password: (可选,长期运行必须)指定自己的QQ密码并自动登陆,在session过期后会自动重新登陆')
    print('    -q (targetQQ) --target-qq: 目标QQ号,使用多个-q来指定多个目标')
    print('    -d (number)  --delay: 两次拉取说说的时间间隔(秒),默认15秒,当指定多于1个目标时会除以目标个数,除后最短3秒')
    print('    -j (url) --jump-url: 用于自动登陆的跳转Url(仅供高级用户使用,大多数用户建议用-s)')
    print('    -v (0-3)  --verbose: verbose level(仅供高级用户) 默认1')
    print()
    print('example1: ' + program_exec_cmd + ' -q  -> object345678901 -q 123456789 -q 223456789 -s 333333333')
    print('  在例1中,会打开firefox让你手动登陆,自身qq号为333333333,\n'
          '设置了三个目标,QQ号分别为 345678901 123456789 223456789')
    print()
    print('example2: ' + program_exec_cmd + ' -q 345678901 -q 123456789 -q 223456789 -s 333333333 -p "yourPassword"')
    print('  在例2中,会打开firefox,并自动登陆,自身qq号为333333333,\n'
          '设置了三个目标,QQ号分别为 345678901 123456789 223456789\n'
          '与例1相比,若指定密码,则会在登录过期后自动重新登陆\n'
          '密码建议用双引号包起来,减少特殊字符无法识别的问题'
          'ps:本程序是开源的,不用担心窃取密码的问题')
    sys.exit(error_code)


def parse_cmdline():
    import sys
    import getopt
    global targetQQlist, ownerQQ, jumpUrl, verbose_level, password
    assert isinstance(targetQQlist, list)
    required_args = {'-s', '-q'}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:p:v:j:q:",
                                   ['help', 'password=', 'verbose=', 'self-login=', 'target-qq=', 'jump-url='])
    except getopt.GetoptError as err:
        # print help information and exit:
        errprint(err)  # will print something like "option -a not recognized"
        usage(1)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(0)
        elif o in ("-q", "--target-qq"):
            targetQQlist.append(a)  # 支持多个目标
            if '-q' in required_args:
                required_args.remove('-q')
        elif o in ("-j", "--jump-url"):
            jumpUrl = a
            rematch = re_search(r'clientuin=(?P<qq>\d+)&', jumpUrl)
            if rematch is not None:
                ownerQQ = rematch.group('qq')
            else:
                errprint('请输入正确的jumpUrl')
                usage(3)
            required_args.remove('-s')
        elif o in ("-v", "--verbose"):
            verbose_level = int(a)
        elif o in ("-s", "--self-login"):
            jumpUrl = None
            ownerQQ = a
            required_args.remove('-s')
        elif o in ("-p", "--password"):
            password = a
        else:
            assert False, "unhandled option"
    if required_args:
        errprint('缺少以下参数:', *required_args)
        usage(4)


def mood_do_like(Sess, tid, targetQQ):
    global token_like
    post_data = {'qzreferrer': 'http://user.qzone.qq.com/%s/mood' % targetQQ
        , 'opuin': ownerQQ
        , 'unikey': 'http://user.qzone.qq.com/%s/mood/%s.1' % (targetQQ, tid)
        , 'curkey': 'http://user.qzone.qq.com/%s/mood/%s.1' % (targetQQ, tid)
        , 'from': '-100'
        , 'fupdate': '1'
        , 'face': '0'
                 }
    infoprint('正在点赞')
    result = Sess.post('http://w.qzone.qq.com/cgi-bin/likes/internal_dolike_app?g_tk=%s' % token_like[targetQQ],
                       data=post_data)
    if '"message":"succ"' in result.text:
        infoprint('点赞成功')
    else:
        errprint('点赞失败,返回值:', result.text)


def handle_new_mood(Sess, create_time, tid, content, targetQQ):
    # TODO: 添加邮件提醒
    importantprint(targetQQ, '发现新的说说 时间:', create_time, '\r\ntid:', tid, '\r\n', content)
    mood_do_like(Sess, tid, targetQQ)


def selenium_driver_init():
    infoprint('正在初始化浏览器')
    try:
        _driver = webdriver.Firefox()
    except Exception as exp:
        errprint('初始化失败. 请检查是否已安装最新版firefox,错误信息:', exp)
        usage()
    return _driver


def login_with_password(driver, qq, password, retry_count=1):
    infoprint('已指定密码,将自动登陆')
    driver.get('http://qzone.qq.com')
    infoprint('等待3秒页面载入')
    sleep(3 * retry_count)
    login_frame = driver.find_element_by_id('login_frame')  # 找到登陆框的iframe
    driver.switch_to_frame(login_frame)  # 切换到iframe
    sleep(0.5 * retry_count)
    temp = driver.find_element_by_id("switcher_plogin")  # 切换到账号密码登陆
    dbgprint(temp.text)
    temp.click()
    sleep(1 * retry_count)
    driver.find_element_by_id("u").clear()
    sleep(0.2 * retry_count)
    driver.find_element_by_id("u").send_keys(qq)  # 填写QQ号
    sleep(1 * retry_count)
    driver.find_element_by_id("p").clear()
    sleep(0.2 * retry_count)
    driver.find_element_by_id("p").send_keys(password)  # 填写密码
    infoprint('等待2秒')
    sleep(2 * retry_count)
    driver.find_element_by_id("login_button").click()
    for _ in range(10):
        sleep(0.5)
        if qq in driver.current_url:
            infoprint('登陆成功')
            break
    else:
        errprint('登陆失败,正在重试')
        driver = login_with_password(driver, qq, password, retry_count + 1)
    return driver


def get_each_targets_token():
    global targetQQlist, token_like, token_list, driver, Sess
    infoprint('现在开始初始化阶段,遍历每一个目标的空间以获取token')
    for qq in targetQQlist:  # 遍历每一个目标
        infoprint('打开QQ', qq, '的空间')
        driver.get('http://user.qzone.qq.com/%s/mood' % qq)
        infoprint('请等待10秒以便初始化完成')
        sleep(10)
        dbgprint(driver.get_cookies())
        # 点赞页面的token
        token_like[qq] = str(driver.execute_script('return QZFL.pluginsDefine.getACSRFToken(url)'))
        dbgprint('QQ:', qq, 'token_like=', token_like[qq])
        # 列表页面的token
        iframe_src = driver.find_element_by_tag_name('iframe').get_attribute('src')
        token_list[qq] = str(driver.execute_script("return QZFL.pluginsDefine.getACSRFToken('%s')" % iframe_src))
        dbgprint('QQ:', qq, 'token_list=', token_list[qq])
        # 将selenium的cookie转到requests中
        Sess.cookies = selenium2requests(driver.get_cookies(), Sess.cookies)
        sleep(2)
    driver.quit()

    dbgprint(Sess.cookies)


# 初始化各种变量和参数
infoprint('正在初始化')
json_code_meaning = {'请先登陆空间': -3000,
                     'Normal': 0}
jumpUrl = ''
targetQQlist = []
delay = 15  # second
latestTid = {}
token_list = {}
token_like = {}
latestTimeUnix = {}
ownerQQ = ''
password = None
verbose_level = 1
infoprint('处理参数')
parse_cmdline()  # here we parse command line
apoutput_set_verbose_level(verbose_level)
infoprint('自身QQ:', ownerQQ, '目标QQ:', *targetQQlist)
targetQQ = targetQQlist[0]
delay = delay / len(targetQQlist) if delay / len(targetQQlist) > 2 else 2
failure_delay = delay  # increase once we failure
dbgprint('delay', delay, v=2)
initFlag = {qq: True for qq in targetQQlist}

# ######初始化Requests######
Sess = session()
Sess.headers.update(
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0",
     })

DEBUG_PROXY = {
    "http": "http://127.0.0.1:8882",
    "https": "http://127.0.0.1:8882",
} if False else {}
Sess.proxies = DEBUG_PROXY
dbgprint('proxy', Sess.proxies)

# ######通过浏览器获取所需cookies和sessions######
driver = selenium_driver_init()
infoprint('初始化Cookies')
if jumpUrl:
    warnprint('请#不要#操作弹出的浏览器')
    driver.get(jumpUrl)
    infoprint('请等待10秒以便初始化完成')
    sleep(10)
elif password is not None:  # 已指定密码, 自动登陆
    driver = login_with_password(driver, ownerQQ, password)
else:  # 未指定密码, 手动登陆
    infoprint('请在弹出的的浏览器中手动登陆')
    driver.get('http://qzone.qq.com')
    # 等待登陆
    while ownerQQ not in driver.current_url:
        sleep(1)
    infoprint('登陆成功')
# ######### 自动获取每个目标的token ############
get_each_targets_token()
# ################ 循环监控新说说并点赞 #######################
i = 0
while True:
    for targetQQ in targetQQlist:  # 遍历每一个目标
        i += 1
        infoprint(i, '#正在获取说说信息 Target:', targetQQ)
        try:
            moodJson = Sess.get(  # 直接请求ajax的目标
                'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=%s&ftype=0&sort=0&pos=0&num=5&replynum=100&g_tk=%s&callback=_preloadCallback&code_version=1&format=jsonp&need_private_comment=1' % (
                    targetQQ, token_list[targetQQ]))
        except Exception as e:
            errprint(targetQQ, '说说信息获取失败,将在', failure_delay, '秒后重试. 错误原因:', e)
            failure_delay += delay
            sleep(failure_delay)
            continue
        dbgprint(moodJson.text[:500])
        try:
            formatJson = json_loads(moodJson.text.replace('});', '}').replace('_preloadCallback(', ''))
        except Exception as e:
            errprint(targetQQ, '无法解析说说内容,将在', failure_delay, '秒后重试. 错误原因:', e, is_beep=True)
            failure_delay += delay
            sleep(failure_delay)
            continue
        if formatJson['code'] == json_code_meaning['请先登陆空间']:  # 登陆失效
            if password is not None:  # 如果指定了密码则重新登陆
                driver = selenium_driver_init()
                driver = login_with_password(driver, ownerQQ, password)
                get_each_targets_token()
        if formatJson['code'] != json_code_meaning['Normal']:  # 返回值不正常,重试
            errprint('返回值不正常:', formatJson['code'], '信息:', formatJson['message'])
            failure_delay += delay
            sleep(failure_delay)
            continue
        firstMoodContent = formatJson['msglist'][0]['content']  # 最新一条说说的内容
        firstMoodTimeUnix = int(formatJson['msglist'][0]['created_time'])  # 最新一条说说的Unix时间戳(来自json)
        firstMoodTid = formatJson['msglist'][0]['tid']  # 最新一条说说的Tid,点赞所必需
        firstMoodTime = strftime("%Y-%m-%d %H:%M:%S", localtime(firstMoodTimeUnix))  # 最新说说的人类可阅读格式时间
        infoprint(targetQQ, '最新说说时间:', firstMoodTime, v=2)
        infoprint(targetQQ, 'tid:', firstMoodTid, v=2)
        infoprint(targetQQ, '最新说说内容:\n', firstMoodContent)

        if initFlag[targetQQ]:  # 初始化
            latestTid[targetQQ] = firstMoodTid
            latestTimeUnix[targetQQ] = firstMoodTimeUnix
            initFlag[targetQQ] = False

        if latestTid[targetQQ] != firstMoodTid:  # 最新一条说说的时间发生变化
            if firstMoodTimeUnix > latestTimeUnix[targetQQ]:  # 发了新的说说
                handle_new_mood(Sess, firstMoodTime, firstMoodTid, firstMoodContent, targetQQ)  # 处理新说说事件
                latestTid[targetQQ] = firstMoodTid
                latestTimeUnix[targetQQ] = firstMoodTimeUnix
            else:
                latestTid[targetQQ] = firstMoodTid  # 删除了一条说说
                latestTimeUnix[targetQQ] = firstMoodTime
                importantprint(targetQQ, '对方删除了一条说说')

        sleep(delay)
        failure_delay = delay  # reset failure_delay
