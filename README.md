# Palp 文档

# 简介

Palp 是一个爬虫框架  
整体使用方式和 scrapy 类似，但有以下特点

- 同一个项目可以存放多个不同的 spider，spider 拥有各自的 settings
- 无感分布式，不需要内网，只需要 redis，分布式与非分布式仅继承的类不同
- 自动 cookiejar 仅需要使用 keep_cookie 即可
- 自带 requests、httpx 两种请求器，并可自定义请求器（同时需要自定义解析器）
- 自动 join url
- 数据、任务防丢，续接（分布式）
- 数据、任务失败后自动回收，启动自动接续（需开启
  ITEM_FAILED_SAVE、ITEM_RETRY_FAILED、REQUEST_FAILED_SAVE、REQUEST_RETRY_FAILED）
- 成功、失败任务自动统计（分布式结束后在 redis 的 stop key 去看）

但有以下注意点：

- 默认不对 item、request 进行去重
- 去重一般为普通去重（默认），也有严格去重（需开启），严格去重时，会有锁、分布式锁

# 安装

```
pip install palp
```

# 创建项目与爬虫

创建项目和爬虫都会去判断文件是否存在  
创建爬虫时，会自动移动到 spiders 文件夹下（查找为 3 个深度）

```
palp create -p xxx
palp create -s xxx 1
```

# spider

目前提供 2 个 spider

- LocalSpider：本地爬虫
- DistributiveSpider：分布式爬虫
- CycleSpider：周期爬虫（根据需求可继承本地、分布式）

## LocalSpider

本地爬虫，不支持分布式

### 创建

【命令】

```
palp create -s baidu 1
```

【结构】

```
"""
Create on 2022-12-12 16:21:10.159221
----------
@summary:
----------
@author:
"""
import palp


class BaiduSpider(palp.LocalSpider):
    spider_name = "baidu"   # 自定义的名字
    spider_domains = []  # 允许通过的域名，默认不限制
    spider_settings = None  # 字典形式或导入形式的设置

    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """
        for i in range(10):
            yield palp.RequestGet("https://www.baidu.com")

    def parse(self, request, response) -> None:
        """
        解析函数

        :param request:
        :param response:
        :return:
        """
        print(response)


if __name__ == '__main__':
    BaiduSpider(thread_count=1).start()

```

### DistributiveSpider

分布式爬虫，需要在设置中增加 redis 连接
【命令】

```
palp create -s baidu 2
```

【结构】  
和普通的一毛一样，只是继承类不同，无成本切换

```
"""
Create on 2022-12-12 16:21:10.159221
----------
@summary:
----------
@author:
"""
import palp


class BaiduSpider(palp.DistributiveSpider):
    spider_name = "baidu"   # 自定义的名字
    spider_domains = []  # 允许通过的域名，默认不限制
    spider_settings = None  # 字典形式或导入形式的设置

    def start_requests(self) -> None:
        """
        起始函数

        :return:
        """
        for i in range(10):
            yield palp.RequestGet("https://www.baidu.com")

    def parse(self, request, response) -> None:
        """
        解析函数

        :param request:
        :param response:
        :return:
        """
        print(response)


if __name__ == '__main__':
    BaiduSpider(thread_count=1).start()
```

## CycleSpider

周期爬虫，使用 mysql 创建任务表，并在爬虫内部获取进行抓取

个人认为，任务需求是多样化的，所以任务表的 task 字段是一个字符串，并且获取的任务是全表字段，这样就可以自定义部分表字段，实现更多需求

注意：继承周期爬虫的【同时需要继承 分布式 或 本地爬虫】才可以执行

含有以下方法：

- initialize_all_task_states：重置所有任务状态为 0
- get_tasks：根据指定状态获取任务
- get_tasks_state0：获取状态为 0 的任务
- get_tasks_state2：获取状态为 2 的任务
- set_task_state：设置指定任务的状态
- set_task_state_running：设置指定任务状态为 1
- set_task_state_done：设置指定任务状态为 2
- set_task_state_failed：设置指定任务状态为 3
- create_mysql_table：创建任务表、记录表
- check_mysql_table_exists：检查表是否存在
- insert_tasks：插入任务（字符串或字符串列表）
- insert_task_record_start：创建记录表的初始记录
- update_task_record：更新记录表任务处理量
- update_task_record_end：更新当前爬虫结束

【示例】  
启用记录中间件（都放在最后面）  
该中间件是一个双继承的中间件，所以两个地方都要引入  
主要作用：

- 自动修改失败、成功的任务状态
- 自动在记录表中添加、修改任务执行情况

注意：请求需要向下传递 task_id=task['id']，即任务表中的 id

```
REQUEST_MIDDLEWARE = {
    1: "palp.middleware.CycleSpiderRecordMiddleware",
}

SPIDER_MIDDLEWARE = {
    1: 'palp.middleware.CycleSpiderRecordMiddleware',
}
```

爬虫继承 CycleSpider

```
import palp


class CycleSpider(palp.LocalSpider, palp.CycleSpider):
    spider_name = "baidu"  # 自定义的名字
    spider_domains = []  # 允许通过的域名，默认不限制
    spider_settings = None  # 字典形式或导入形式的设置
    spider_table_task_name = f'palp_cycle_task_{spider_name}'  # 任务表
    spider_table_record_name = f'palp_cycle_record_{spider_name}'  # 记录表

    def start_requests(self) -> None:
        self.initialize_all_task_states()  # 重置所有任务状态为 0

        # 获取任务状态为 0 的任务
        for task in self.get_tasks_state0():
            print(task)
            yield palp.RequestGet(url=task['task'], task_id=task['id'])

    def parse(self, request, response) -> None:
        print(response)


if __name__ == '__main__':
    CycleSpider.create_mysql_table()  # 快捷创建表
    CycleSpider.insert_tasks(['https://www.baidu.com', 'https://www.jd.com'])  # 快捷插入任务
    CycleSpider(thread_count=1).start()
```

# 启动爬虫

## 爬虫内启动

```
BaiduSpider(thread_count=1).start() # 启动可选参数看源码，就几个
```

## 启动文件启动

注意：是进程形式启动，推荐直接使用 start.py 即可，可同时启动多个爬虫

参数介绍

- spider_name：爬虫名（spider 内一致）
- count：启动多少个实例（可实现单机分布式，就是进程启动多少个）
- **kwargs：爬虫启动参数，同 spider 的启动参数

【示例】

```
from palp import start_spider


def main():
    start_spider.execute(spider_name='xxx', count=1)
 
 
if __name__ == '__main__':
    main()
```

# 数据库连接

通过 quickdb 模块，内置了 redis、mongo、mysql、kafka、postgresql 的连接，引用方式如下：

```
from palp import conn
conn.redis_conn # 接原始命令
conn.pg_conn    # 基于 sqlalchemy 魔改版本
conn.mysql_conn # 基于 sqlalchemy 魔改版本
conn.mongo_conn # 基于 mongo_conn 添加了部分方法，如 iter
conn.kafka_conn # kafka_conn.send 即可
```

注意：内置了 SpiderRecycleMiddleware 中间件，创建的连接会自动关闭

具体的使用可以看 quickdb 模块，这里强烈推荐 quickdb 针对 sqlalchemy 的数据库模板导出功能：

```
from quickdb import PostgreSQLAlchemyEngine

pg_conn = PostgreSQLAlchemyEngine(
    host=settings.PG_HOST,
    port=settings.PG_PORT,
    db=settings.PG_DB,
    user=settings.PG_USER,
    pwd=settings.PG_PWD,
    **settings.PG_CONFIG
)
pg_conn.reverse_table_model(path='./models.py', tables=['xxx'])  # path 可以自动生成
```

# Middleware

## SpiderMiddleware

这是项目中间件，可通过 spider 访问到对应的属性

- spider_start：爬虫启动时干什么
- spider_error：爬虫出错时干什么
- spider_close：爬虫结束时干什么（必定会执行）

【结构】

```
import palp
from loguru import logger


class SpiderMiddleware(palp.SpiderMiddleware):
    def spider_start(self, spider) -> None:
        """
        spider 开始时的操作

        :param spider:
        :return:
        """

    def spider_error(self, spider, exception: Exception) -> None:
        """
        spider 出错时的操作

        :param spider:
        :param exception: 错误的详细信息
        :return:
        """
        logger.exception(exception)

    def spider_close(self, spider) -> None:
        """
        spider 结束的操作

        :param spider:
        :return:
        """
```

【添加到设置中】
注意：这里的 1 代表顺序

```
SPIDER_MIDDLEWARE = {
    1: 'middlewares.middleware.SpiderMiddleware',
}
```

## RequestMiddleware

请求中间件

- request_in：请求创建时干什么
- request_error：请求出错时干什么（默认重试 3 次 settings.REQUEST_RETRY_TIMES）
- request_failed：请求失败时干什么（3 次后还失败，走这里）
- request_close：请求结束时干什么（执行完毕后走这里）

注意：

- request_failed 和 request_close 只有走其中一个
- 不要的请求可直接抛出 DropRequestException 错误
- 请求可以原地修改
- request_error 可以判断错误进行修改，或者直接 return 新的请求，旧请求自动丢弃
- request_close 可以判断响应是否符合预期，或者直接 return 新的请求，旧请求自动丢弃

提示：分布式爬虫时，设置开启以下两个选项，即可自动保存错误请求，并存放 redis，下次请求自动继续

- REQUEST_FAILED_SAVE = True # 分布式时保存失败的请求（重试之后仍然失败的）
- REQUEST_RETRY_FAILED = True # 分布式时启动重试失败请求

【结构】

```
import palp
from typing import Union
from palp import settings
from loguru import logger
from palp.network.request import Request

class RequestMiddleware(palp.RequestMiddleware):
    def request_in(self, spider, request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """
        if settings.REQUEST_PROXIES_TUNNEL_URL:
            request.proxies = {
                'http': settings.REQUEST_PROXIES_TUNNEL_URL,
                'https': settings.REQUEST_PROXIES_TUNNEL_URL,
            }

    def request_error(self, spider, request, exception: Exception) -> Union[Request, None]:
        """
        请求出错时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param exception: 错误的详细信息
        :return: [Request, None]
        """
        logger.exception(exception)

        return

    def request_failed(self, spider, request) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param request:
        :return:
        """
        logger.warning(f"失败的请求：{request}")

    def request_close(self, spider, request, response) -> Union[Request, None]:
        """
        请求结束时的操作

        :param spider:
        :param request: 该参数可返回（用于放弃当前请求，并发起新请求）
        :param response:
        :return: [Request, None]
        """
        return

```

【添加到设置中】
注意：这里的 1 代表顺序

```
REQUEST_MIDDLEWARE = {
    1: "middlewares.middleware.RequestMiddleware",
}
```

### 添加代理

注意：这里基于默认的 ResponseDownloaderByRequests 请求器（requests）

```
class RequestMiddleware(palp.RequestMiddleware):
    def request_in(self, spider, request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """
        
        # 给所有 url 都添加代理
        if settings.REQUEST_PROXIES_TUNNEL_URL:
            request.proxies = {
                'http': settings.REQUEST_PROXIES_TUNNEL_URL,
                'https': settings.REQUEST_PROXIES_TUNNEL_URL,
            }
           
        # 指定域名添加代理
        allow_domains = ['xxx']
        
        if settings.REQUEST_PROXIES_TUNNEL_URL:
            if request.domain in allow_domains:
                request.proxies = {
                    'http': settings.REQUEST_PROXIES_TUNNEL_URL,
                    'https': settings.REQUEST_PROXIES_TUNNEL_URL,
                }
```

# Pipeline

处理 item，清洗、入库，含有以下方法

- pipeline_in：数据进入时，一般用作清洗
- pipeline_save：数据保存方法，一种保存写一个清晰明了
- pipeline_error：数据保存出错时，默认重试次数 3 ，可通过 settings.PIPELINE_RETRY_TIMES 设置
- pipeline_failed：数据保存出错超过最大次数
- pipeline_close：无数据时，整个 pipeline 结束时运行！！！

注意：

- 数据都是原地修改的，不需要传递
- 默认启动的数据处理线程是 5，可通过 settings.ITEM_THREADS 调整
- 默认是单条传递，有多条传递需求的可通过 PIPELINE_ITEM_BUFFER 调整，这样传递 item 的就是列表
- 不需要的 item 可以通过 DropItemException 进行丢弃，但如果是多条直接在 item 列表移除就行，丢弃的话整个都会被丢掉

【结构】

```
import palp
from loguru import logger


class Pipeline(palp.Pipeline):
    def pipeline_in(self, spider, item) -> None:
        """
        入库之前的操作，一般是清洗

        :param spider:
        :param item:
        :return:
        """

    def pipeline_save(self, spider, item) -> None:
        """
        入库

        :param spider:
        :param item: 启用 item_buffer 将会是 List[item] 反之为 item
        :return:
        """
        logger.info(item)

    def pipeline_error(self, spider, item, exception: Exception) -> None:
        """
        入库出错时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :param exception: 错误的详细信息
        :return:
        """
        logger.exception(exception)

    def pipeline_failed(self, spider, item) -> None:
        """
        超过最大重试次数时的操作

        :param spider:
        :param item: 启用 item buffer 时是 List[item]
        :return:
        """
        logger.warning(f"失败的 item：{item}")

    def pipeline_close(self, spider) -> None:
        """
        spider 结束时的操作

        :param spider:
        :return:
        """

```

【添加到设置中】
注意：这里的 1 代表顺序

```
PIPELINE = {
    1: "pipelines.pipeline.Pipeline",
}
```

# Item

通过 yield item 将数据发送到 pipeline 进行保存  
Item 提供了两种

- Item
- StrictItem

## Item

懒人 item 不需要定义字段，但是最好有多个就写不同的名字做区分  
【创建】

```
import palp


class Item(palp.Item):
    """
        通用、懒人 item
    """
```

【使用】

```
yield Item(**{'xxx':'yyy'})
```

## StrictItem

严格 item，需要定义哪些字段被允许通过

```
import palp

class StrictItem(palp.StrictItem):
    """
        严格 item
    """
    # 此处需要定义数据库字段
    # name = palp.Field()
```

【使用】

```
yield StrictItem(**{'xxx':'yyy'})
```

# Request

提供了以下方法

- RequestGet
- RequestPost
- RequestDelete
- RequestOptions
- RequestHead
- RequestPatch

除了 requests、httpx 参数常用外，还可以通过 command 指定其它参数，方便自定义请求器时使用

框架的参数如下

- downloader：局部下载器（不需要实例化）
- downloader_parser：局部下载解析器（不需要实例化）
- filter_repeat：是否过滤请求（默认不过滤）
- keep_session：是否保持 session 自动 cookie，tls 连接
- keep_cookie：自动 cookieJar
- new_session：创建新的 session
- callback：回调函数（必须有）
- cookie_jar：cookieJar（用户不需要手动操作，但是可以通过该参数获取值）
- priority：使用优先级队列时的优先级（默认就是优先级队列，默认优先级 settings.DEFAULT_QUEUE_PRIORITY）
- command：自定义请求器时的传参字典

注意：

- 请求过滤默认是不开启的，需要开启 settings.FILTER_REQUEST（普通过滤）
- 在开启普通过滤的情况下，可以选择开启 settings.STRICT_FILTER（严格过滤）加锁，严重影响性能，不推荐
- keep_session 虽然可以提高部分效率，但是除非你对 cookie 要求不高，否则分布式 cookie 无法随着请求发到其他机器
- keep_session 时，如果需要创建新的 session，那就需要 new_session=True 重新创建
- keep_cookie 推荐，类似 scrapy 手动使用 cookiejar，这里只要一直 keep_cookie=True 就行
- 请求队列默认是 优先级队列，想修改通过 settings.REQUEST_QUEUE_MODE 修改
- 优先级队列，本身就有过滤重复请求的作用！！！

# Response

请求响应
提供了自带的以下方法

- xpath
- css
- re
- re_first
- bs4（默认解析器：lxml）
- urljoin：合并 url，可以手动使用（默认会自动处理）

【示例】

```
def parse(self, request, response) -> None:
    """
    解析函数

    :param request:
    :param response:
    :return:
    """
    response.bs4.find()
    response.re()
    response.re_first()
    response.xpath().extract()
    response.xpath().extract_first()
```

# alarm

基于 gsender 模块的内置报警  
提供两个函数

- send_email：发送邮件
- send_dingtalk：支持所有钉钉群聊消息类型

修改设置

```
# 预警：Email
EMAIL_USER = None  # Email 账号
EMAIL_PWD = None  # Email 授权码

# 预警：DingTalk
DING_TALK_SECRET = None  # 加签
DING_TALK_ACCESS_TOKEN = None  # webhook 链接内的 access_token
```

注意：

- 模块需要主动调用
- 钉钉消息考虑到模板较多，所以返回的是 DingTalkSender 对象，再去调用对应的发送方法

【示例】

```
import palp

palp.send_email(receiver='xxx', content_text='palp 执行结束')
palp.send_dingtalk().send_text(content='测试消息')
```

# M、其它使用技巧

## 1、增量爬虫

增量无非就是判断，建议拿主键直接判断，下面有两个简单的例子

### 1.1 数据库判断

即通过自己保存的数据，进行判断列表页，已出现的 url 则为已抓取，那么后续则不需要抓取  
【案例】

```
is_repeat = False   # 重复标志

for i in response.xpath('//ul[@class="list_con"]//li'):
    notice_url = response.urljoin(i.xpath('./a/@href').extract_first())
    
    # 判断是否重复
    if conn_company_notice.find_one({'notice_url': notice_url}):
        is_repeat = True
        break
    
    yield palp.RequestGet(url=notice_url, callback=self.parse_content)

# 翻页
if not is_repeat and page_now < page_total:
    pass
```

### 1.2 redis 判断

Palp 默认的分布式去重有：

- redis set 去重
- redis bloom 去重（默认）

对应的过滤器如下：

- RedisSetFilter：对应 redis set 去重
- RedisBloomFilter：对应 redis bloom 去重

使用时需开启以下设置，作用是开启去重并持久化

```
FILTER_REQUEST = True
PERSISTENCE_REQUEST_FILTER = True
```

【案例】以 redis bloom 去重 为例  
注意：虽然本身会做去重请求，但是之所以这样写，是为了避免再去翻页浪费时间

```
from palp.filter import RequestRedisBloomFilter

is_repeat = False   # 重复标志

for i in response.xpath('//ul[@class="list_con"]//li'):
    notice_url = response.urljoin(i.xpath('./a/@href').extract_first())
    
    req = palp.RequestGet(url=notice_url, callback=self.parse_content)

    # 判断是否重复
    if RequestRedisBloomFilter().is_repeat(req):
        break
    
    yield req

# 翻页
if not is_repeat and page_now < page_total:
    pass
```

## 2、快速二次请求

基于上一次请求的基础上进行二次请求  
有两种方法：

- 原地修改
- request 的 to_dict() 方法获取字典后修改

### 2.1、原地修改

```
def parse(self, request, response) -> None:
    request.xxx = xxx   # 修改

    yield request
```

### 2.2、to_dict()

```
request_dict = request.to_dict()
request_dict[xxx] = xxx # 修改

yield palp.Request(**request_dict)
```

## 3、个性化爬虫

比如批次爬虫，根据 redis 获取任务，其实很简单的（不内置批次爬取爬虫）

### 关于表

可以设置多种状态：已抓取，待抓取，队列中，等等  
大概流程如下：

- 不论你什么需求，只要在 start_requests 函数中，设置获取方法
- 随后设置为队列中状态
- 在 pipeline 中设置修改已爬取状态

### 关于 redis

可以设置最简单的 list、或者不重复的 set 或者优先级的 zset  
只要在 start_requests 函数中 直接执行对应的 pop 方法不就行了