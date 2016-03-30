# 多进程分布式数据采集演示

为了演示分布的多进程数据采集服务的设计架构，使用`python`语言简单的实现了通过给定搜索关键字及手动选择分布式节点抓取weibo.cn及medium.com的文章数据并存储至`mongodb`数据库的演示程序。整个系统在功能上分为两大块：

- 数据采集模块：根据待采集的网站信息，编写不同的采集规则实现；
- 分布式任务模块：采用管理主服务与采集节点服务的方式实现分布式任务的发送及执行；

## 数据采集设计

### weibo.cn

通过分析weibo.cn的查询页面，获取了weibo.cn的数据查询ajax调用请求地址为：`http://m.weibo.cn/page/pageJson`，并且该请求地址能返回完整的json数据格式；完整的请求地址示例：

	http://m.weibo.cn/page/pageJson?containerid=100103type%3D%26q%3D李沁&v_p=11&ext&fid=100103type%3D%26q%3D李沁&uicode=10000011&next_cursor&page=1
根据上述的地址示例能清楚的分析到，`containerid=100103type%3D%26q%3D李沁`及`fid=100103type%3D%26q%3D李沁`为查询关键字参数；同时`page=1`为页码参数，使用模拟http get请求的方式循环请求就可以获得相关数据了，由于数据量比较大可以自行请求查看效果。

通过对返回结果的json数据进行分析，可以获得如下简单的数据结构说明：

1. `cards`数据节点中存储放在所有的业务数据，并且`itemid`为hotmblog及mblog的数据节点存放着微博信息；
2. `cards`的子节点里的`card_group`存储着每条微博的详细信息；
3. `card_group`的子节点`mblog`存储微博的文章信息；
4. `card_group`的子节点`user`存储着发布者的信心；

### medium.com

通过分析medium.com的查询页面，获取了medium.com的数据查询地址虽然也是采用ajax方式和返回json数据的，但是由于该网站在http cookies里写入了相关信息无法通过模拟请求的方式直接获取json数据，故采用传统的dom解析的方式进行数据采集；查询数据接口地址为：`https://medium.com/search/posts`，该请求地址返回的是传统的html格式；完整的请求地址示例：

	https://medium.com/search/posts?q=java&count=10&ignore=ab67fc68eb0b&ignore=6fa6bdf5ad95&ignore=48d4011b6fc4&ignore=d14f0585d05e&ignore=db8163bc6798&ignore=78dbcc1fbcaa&ignore=448a00fa672d&ignore=457306e6bc1c&ignore=c00503d0913e&ignore=23cbe49186e8
	
根据上述的地址示例能清楚的分析到，`q=java`为查询关键字；`count=10`为分页总数（但实际测试中，该参数并无效果）；`ignore=48d4011b6fc4...`为上一页的数据主键，所以该网站接口是不支持跳页请求的，要通过忽略前面页数的请求来达到跳页采集的效果。由于html数据量比较大可以自行请求查看效果。

通过返回的结果页面进行分析，可以获取如下简单的页面结构说明：

1. `div.blockGroup-list > div.block`路径下存储着文章的id信息，用于翻页时使用；
2. `div.blockGroup-list > div.block > div.block-streamText > div.block-content > article > a`路径下存储着文章的页面信息，用于请求页码获取页面数据；
3. 文章详情页面的`div.section-content > div.section-inner.layoutSingleColumn`路径下存储着文章的标题与内容；
4. 文章详情页面的`a.link.link.link--darken`路径下存储着作者的名称；
5. 文章详情页面的`button[data-action="show-recommends"]`路径下存储着收藏总数；
6. 文章详情页面的`button[data-action="scroll-to-responses"]`路径下最后一个匹配节点存储着回复总数；

## 分布式设计

考虑到数据采集一般都采用分布式的形式进行设计，能保证在大量数据抓取采集时能大幅提高采集效率缩短采集时间，所以设计之初就采用任务管理与采集节点分离的方式来实现整个系统架构。整个系统可以独立部署到不同的服务器主机上，程序内置两个不同的启动器：

1. 任务管理主服务；
2. 采集节点服务；

根据实际业务需要，可以部署多个任务管理主服务及多个采集节点服务，只是选择不同的启动器就可以实现不同服务的切换。具体实现流出如下：

1. 采集节点服务通过请求任务管理主服务注册自己并告知任务管理服务自己主机地址、端口、名称等信息；任务管理主服务会存储或更新该采集节点的信息；
2. 任务管理主服务创建任务时，必须要选择采集节点进行数据采集。创建任务成功后，任务管理主服务根据数据库存储的节点信息，向该采集节点服务发送任务信息进行数据采集；
3. 采集节点接受到任务信息后，根据任务信息中所包含的采集参数选择不同的采集接口实现进行数据采集；
4. 采集完成后通知任务管理主服务任务已完成；

## 安装部署

### 运行环境

- Python 2.7
- Flask 0.10.1
- Flask-Cors 2.1.2
- requests 2.9.1
- beautifulsoup4 4.4.1
- pymongo 3.2.2
- pytest 2.9.1
- Mongdb 3.2.4

推荐使用`pip`安装`python`的安装依赖环境，`pip`安装教程具体见[官网](http://pip-cn.readthedocs.org/en/latest/installing.html)；

安装完成后使用`http://127.0.0.1:9000/tasks`地址进行访问；

### 配置文件

配置文件位于工程根目录下的`config.py`文件：

	SERVER = {
	    # 任务管理主服务的请求地址，用于采集节点服务使用
	    "URL": "http://127.0.0.1:9000",
	    # 任务管理主服务的运行端口
	    "PORT": 9000,
	    # 开启flask调试状态
	    "DEBUG": True
	}
	
	NODE = {
	    # 采集节点的运行端口
	    "PORT": 9001,
	    # 开启flask调试状态
	    "DEBUG": True
	}
	
	MONGO = {
	    # 数据库主机地址
	    "HOST": "localhost",
	    # 数据库端口
	    "PORT": "27017",
	    # 数据库名称
	    "DB": "crawler_db"
	}

### 手动部署

请确保当前环境已安装了`python2.7`、`pip`、`mongodb`，然后根据以下步骤进行部署安装：

1. 获取工程源码：`https://github.com/yejianfei/multi-process-crawler.git`
2. 进入工程目录，使用`pip`安装第三方依赖，执行命令：`pip install -r requirements.txt`
3. 根据实际情况修改配置文件；
4. 启动任务管理主服务：`python server.py`
5. 启动采集节点服务：`python task.py`

### 安装脚本

安装脚本用于执行curl命令获取源码及安装依赖环境等操作，目前部署脚步只支持Ubuntu Linux及Mac OSX发行版。
	
	d
	

### 容器化部署

>***开发中***


## 未来改进

- 数据采集结果的查看；
- 目标只要创建及删除任务，应该提供诸如：启动，停止，定时等功能；
- 提供数据采集过程实时监控的功能，目前只能接受到任务完成通知；
- 提供自动负载与轮询的方式，实现自动选择采集节点的功能；



