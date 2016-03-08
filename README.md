# ShuoshuoMonitor  
---
`version 0.7.9`  
监控别人的说说,并在对方新发说说时给予秒赞  
支持多个目标  
在运行时会先打开firefox(需要手动登陆QQ空间)，然后在自动获取cookies后关掉firefox,此后均不需要浏览器  
支持在对方有新说说时通过QQ消息/手机短信实时通知自己  
tips:建议丢到windows server上运行
  
## 下载与运行  
---
#### 如果你是电白
 - 安装[firefox](http://www.firefox.com.cn/)  
 - 点右边的链接下载电白专用运行包  https://github.com/Aploium/ShuoshuoMonitor/releases/download/v0.7.0/ShuoshuoMonitor_v0.7.0.zip  
   - 必须先全部解压才能运行  
   - 在压缩包里直接双击的蠢货们,你们一定嫁不出去的  
 - __解压__后运行`ShuoshuoMonitor.exe`  

#### 如果你会用Python
 - 安装[firefox](http://www.firefox.com.cn/)  
 - 安装[Python 3.x](https://www.python.org/downloads/)建议安装3.5,安装时记得勾选`add to path`  
 - 点网页右上`Download ZIP`下载Python源码后运行`python shuoshuo.py`  
   


## 参数  
    -h --help: 显示帮助  
    -s (selfQQ) --self-login: 指定自己的QQ并手动在浏览器中登陆  
    -q (targetQQ) --target-qq: 目标QQ号,使用多个-q来指定多个目标  
    -d (number)  --delay: 两次拉取说说的时间间隔(秒),默认10秒,当指定多于1个目标时会除以目标个数,除后最短2秒  
    -j (url) --jump-url: 用于自动登陆的跳转Url(仅供高级用户使用,大多数用户建议用-s)  
    -v (0-3)  --verbose: verbose level(仅供高级用户) 默认1  
 
## 运行  
---
#### 使用exe包的小伙伴:
双击解压出来的`ShuoshuoMonitor.exe`  
在打开的窗口中输入
`ShuoshuoMonitor.exe -q 345678901 -q 123456789 -q 223456789 -s 333333333`
  
#### 直接使用python的小伙伴: 
`python shuoshuo.py -q 345678901 -q 123456789 -q 223456789 -s 333333333`  
  
  
在上例中,会打开firefox让你手动登陆,自身qq号为333333333
设置了三个目标,QQ号分别为 345678901 123456789 223456789  
(均根据实际修改,若想测试,可以把目标设置为自己,然后自己发一条新说说看效果)  

## 运行需求  
---
 - firefox  
 - requests (一个python模块,已内置)  
 - selenium (一个python模块,已内置)  

## 已知问题  
 - session会在大约5天后失效，此后需要重新登录  
 
## QQ消息通知与短信通知
这两个功能是由内置的[ColorfulPyPrint模块](https://github.com/Aploium/ColorfulPyPrint)提供的  
  
QQ消息通知需要自己的WebQQ消息服务端,服务端的运行(相当傻瓜化)见[WebQQ_API](https://github.com/Aploium/WebQQ_API)  
短信通知使用了[阿里大鱼](http://www.alidayu.com/)的短信接口  
