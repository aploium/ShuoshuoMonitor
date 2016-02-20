# ShuoshuoMonitor  
---
`version 0.6.0`  
监控别人的说说,并在对方新发说说时给予秒赞  
  
在运行时会先打开firefox(需要手动登陆QQ空间)，然后在自动获取cookies后关掉firefox,此后均不需要浏览器  
tips:建议丢到windows server上运行

## 运行需求  
---
 - firefox  
 - requests (一个python模块,已内置)  
 - selenium (一个python模块,已内置)  
  
## 安装  
---
 - 安装[firefox](http://www.firefox.com.cn/)  
 - 安装[Python 3.x](https://www.python.org/downloads/)建议安装3.5,安装时记得勾选`add to path`  
   

## 参数  
    -h --help: 显示帮助  
    -s (selfQQ) --self-login: 指定自己的QQ并手动在浏览器中登陆  
    -q (targetQQ) --target-qq: 目标QQ号  
    -d (number)  --delay: 两次拉取说说的时间间隔(秒),默认10秒  
    -j (url) --jump-url: 用于自动登陆的跳转Url(仅供高级用户使用,大多数用户建议用-s)  
    -v (0-3)  --verbose: verbose level(仅供高级用户) 默认1  
 
## 运行  
例子,其中345678901是目标QQ号,333333333是自己的QQ  
`python shuoshuo.py -q 345678901 -s 333333333`  

## 已知问题  
 - session会在大约24小时后失效，此后需要重新登录  

## TODO  
 - 在对方有新说说时用邮件通知自己  
 - 给定自己QQ的账号密码,在session失效后自动重新登录  
