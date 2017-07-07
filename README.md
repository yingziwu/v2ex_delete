# v2ex删贴监测系统

## 初衷
[v2ex](https://www.v2ex.com/)一直把不能删贴、不能删回复作为社区的一个特色。

我一开始也是认为v2ex是不会删贴的，顶多是把帖子移动到特殊节点。  
后来发现v2ex也删贴，我感到有一点失望，但也对这种做法表示理解，毕竟已经在国内备案，做出一点妥协也是可以理解的。

直到有一天我发现 [/t/349115](https://www.v2ex.com/t/349115) 发布不久便被删除了，这让我感到了欺骗。  
于是，我萌生了写一个v2ex删贴监测系统的想法。

## 关于v2ex删贴

发布第一期删贴统计后，引发了[一些讨论](https://www.v2ex.com/t/368217)。  

有同学提醒应该加上一些说明，防止出现一些误会。  
现在关于v2ex删贴的事加上我的一些说明。

- V2EX 从来没有没有说过“绝对不删帖”。关于删除，更确切的规则是，这里的用户在发布了主题或者回复之后，自己无法删除或者修改。 *[注1](#note1)*
-  一些删贴的情况：*[注2](#note2)*
    1. Spam 是会彻底删除的
    1. 有部分 0 回复主题根据发帖者要求被删除
    1. [/go/sandbox](https://www.v2ex.com/go/sandbox) 里的帖子会被不定时清理
    1. 涉及人身攻击、极端政治言论的帖子也会被删除
    1. 某些特殊原因（如律师信等情况）也会被删除

<a name="note1"></a>**注1：**   
https://www.v2ex.com/t/368217#r_4423842

<a name="note2"></a>**注2：**   
https://www.v2ex.com/t/192635#r_2079456  
https://www.v2ex.com/t/231563#r_2568942

## 使用方法

### 安装Redis
Ubuntu
```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get -y install redis-server
```
其他系统可参见：https://redis.io/topics/quickstart

### 安装依赖
```
$ pip3 install -r requirements.txt
$ pip3 install requests[socks]
```

### 创建数据库
使用`sql/create_table.sql`，通过sqlite3创建数据库。

### 修改配置文件
```
$ cp settings.py.example settings.py
```
修改`settings.py`，填入v2ex帐户（建议使用小号），添加User-Agent，根据情况修改代理设置，修改数据库所在路径。

修改`Run.sh`，将`/home/arch/python/v2ex_delete`替换为项目所在路径。

### 添加crontab
将`Run.sh`添加至crontab。  
如：`* * * * * bash /home/arch/python/v2ex_delete/Run.sh`

进行此步前，请确保`redis-server`已经运行。

### 启动rqworker
在项目目录下运行
```
./Start_rqworker.sh
```

## 使用建议
1. 为降低被封概率，请添加代理、UA。
1. 对于重要请求尽量不使用代理，如使用请保证代理的稳定性。
1. 对于一般请求请使用代理以免主ip被封。根据经验10个**稳定的**代理，便可以满足要求。
1. 请根据代理的稳定性，调整failed队列worker数量。请求失败率高，请增加worker数量。
1. 请定期监控项目的工作情况（`rqinfo`），如failed队列过长，请及时检查代理情况。
1. 本项目有两种抓取模式，`Mode1`与`Mode2`，`Mode2`请求更少，效果相比`Mode1`稍差，建议在无代理或代理较少的情况下使用`Mode2`。
1. 该项目默认设置为两周后开始检测删贴，如需修改，可修改`run.py`中`tester_tasker`函数中的SQL语句。
