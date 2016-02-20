# -*- coding: utf-8 -*-
from json import loads as json_loads
from re import search as re_search
from time import sleep, strftime, localtime
from cookies_convert import selenium2requests

try:
    from ColorfulPyPrint import *
except:
    from _ColorfulPyPrint import *
try:
    from selenium import webdriver
except:
    errprint('需要selenium包的支持,请安装: pip install selenium')
try:
    from requests import session, Response as reqResponse, get
except:
    errprint('requests,请安装: pip install requests')

__version__ = '0.6.3'
jumpUrl = ''
targetQQ = ''
delay = 10  # second


def usage():
    global __version__
    from os.path import basename
    print('说说监控及秒赞工具 Version: %s' % __version__)
    print('### 本程序需要系统已安装firefox ###')
    print('    -h --help: 显示本帮助')
    print('    -s (selfQQ) --self-login: 指定自己的QQ并手动在浏览器中登陆')
    print('    -q (targetQQ) --target-qq: 目标QQ号')
    print('    -d (number)  --delay: 两次拉取说说的时间间隔(秒),默认10秒')
    print('    -j (url) --jump-url: 用于自动登陆的跳转Url(仅供高级用户使用,大多数用户建议用-s)')
    print('    -v (0-3)  --verbose: verbose level(仅供高级用户) 默认1')
    print()
    print('example:    python ' + basename(__file__) + ' -q 345678901 -s 358890739')


def PraseCmdline():
    import sys
    import getopt
    global targetQQ, ownerQQ, jumpUrl, is_debug, verbose_level
    required_args = {'-s', '-q'}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:v:j:q:",
                                   ['help', 'verbose=', 'self-login=', 'target-qq=', 'jump-url='])
    except getopt.GetoptError as err:
        # print help information and exit:
        errprint(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-q", "--target-qq"):
            targetQQ = a
            required_args.remove('-q')
        elif o in ("-j", "--jump-url"):
            jumpUrl = a
            ownerQQ = re_search(r'clientuin=(?P<qq>\d+)&', jumpUrl).group('qq')
            required_args.remove('-s')
        elif o in ("-v", "--verbose"):
            verbose_level = int(a)
        elif o in ("-s", "--self-login"):
            jumpUrl = None
            ownerQQ = a
            required_args.remove('-s')
        else:
            assert False, "unhandled option"
    if required_args:
        errprint('缺少以下参数:', *required_args)
        usage()
        sys.exit(2)


def mood_do_like(Sess, tid):
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
    result = Sess.post('http://w.qzone.qq.com/cgi-bin/likes/internal_dolike_app?g_tk=%s' % token_like, data=post_data)
    if '"message":"succ"' in result.text:
        infoprint('点赞成功')
    else:
        errprint('点赞失败,返回值:', result.text)


def handle_new_mood(Sess, create_time, tid, content):
    # TODO: 添加邮件提醒
    global token
    importantprint('发现新的说说 时间:', create_time, '\r\ntid:', tid, '\r\n', content)
    mood_do_like(Sess, tid)


infoprint('正在初始化')
initFlag = True
latestTid = ''
ownerQQ = ''
latestTimeUnix = 0
verbose_level = 1
infoprint('处理参数')
PraseCmdline()
infoprint('自身QQ:', ownerQQ, '目标QQ:', targetQQ)
apoutput_set_verbose_level(verbose_level)
targetQZoneUrl = 'http://user.qzone.qq.com/%s/mood' % targetQQ

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

# ######通过浏览器获取所需cookies和sessions######
infoprint('通过浏览器获取所需cookies和sessions')
try:
    driver = webdriver.Firefox()
except Exception as e:
    errprint('初始化失败. 请检查是否已安装最新版firefox,错误信息:', e)
    exit()
infoprint('初始化Cookies')
if jumpUrl:
    warnprint('请#不要#操作弹出的浏览器')
    driver.get(jumpUrl)
    infoprint('请等待10秒以便初始化完成')
    sleep(10)
else:
    infoprint('请在弹出的的浏览器中手动登陆')
    driver.get('http://qzone.qq.com')
    # 等待登陆
    while ownerQQ not in driver.current_url:
        sleep(1)
    infoprint('登陆成功')
infoprint('打开对方空间')
driver.get(targetQZoneUrl)
infoprint('请等待10秒以便初始化完成')
sleep(10)
dbgprint(driver.get_cookies())
# 点赞页面的token
token_like = str(driver.execute_script('return QZFL.pluginsDefine.getACSRFToken(url)'))
dbgprint('token_like=', token_like)
# 列表页面的token
iframe_src = driver.find_element_by_tag_name('iframe').get_attribute('src')
token_list = str(driver.execute_script("return QZFL.pluginsDefine.getACSRFToken('%s')" % iframe_src))
dbgprint('token_list=', token_list)
# 将selenium的cookie转到requests中
Sess.cookies = selenium2requests(driver.get_cookies(), Sess.cookies, is_clear_all=True)
sleep(2)
driver.quit()

dbgprint(Sess.cookies)
i = 0
while True:
    i += 1
    infoprint(i, '#正在获取说说信息 Target:', targetQQ)
    moodJson = Sess.get(
        'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=%s&ftype=0&sort=0&pos=0&num=5&replynum=100&g_tk=%s&callback=_preloadCallback&code_version=1&format=jsonp&need_private_comment=1' % (
            targetQQ, token_list))
    dbgprint(moodJson.text[:500])
    formatJson = json_loads(moodJson.text.replace('});', '}').replace('_preloadCallback(', ''))
    firstMoodContent = formatJson['msglist'][0]['content']
    firstMoodTimeUnix = int(formatJson['msglist'][0]['created_time'])
    firstMoodTime = strftime("%Y-%m-%d %H:%M:%S", localtime(firstMoodTimeUnix))
    firstMoodTid = formatJson['msglist'][0]['tid']
    infoprint('最新说说时间:', firstMoodTime, v=2)
    infoprint('tid:', firstMoodTid, v=2)
    infoprint('最新说说内容:\n', firstMoodContent)

    if initFlag:  # 初始化
        latestTid = firstMoodTid
        latestTimeUnix = firstMoodTimeUnix
        initFlag = False

    if latestTid != firstMoodTid:
        if firstMoodTimeUnix > latestTimeUnix:  # 发了新的说说
            handle_new_mood(Sess, firstMoodTime, firstMoodTid, firstMoodContent)
            latestTid = firstMoodTid
            latestTimeUnix = firstMoodTimeUnix
        else:
            latestTid = firstMoodTid
            latestTimeUnix = firstMoodTime
            importantprint('对方删除了一条说说')

    sleep(delay)
