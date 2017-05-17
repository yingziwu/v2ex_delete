# v2ex删贴监测系统

## 初衷
[v2ex](https://www.v2ex.com/)一直把不能删贴、不能删回复作为社区的一个特色。

我一开始也是认为v2ex是不会删贴的，顶多是把帖子移动到特殊节点。  
后来发现v2ex也删贴，我感到有一点失望，但也对这种做法表示理解。

直到有一天我发现 [/t/349115](https://www.v2ex.com/t/349115) 发布不久便被删除了，这让我感到了欺骗。  
我萌生了写一个v2ex删贴监测系统的想法。

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
1. 建议尽可能多的添加代理、添加UA。
1. 该所需时间项目较长，请耐心等待。启动后，两周后可查看第一批删贴监测结果。
