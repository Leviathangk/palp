"""
    配置
        配置优先级 spider > spider setting > palp setting
        三者的配置是覆盖的关系
"""
from pathlib import Path

BASE_PATH = Path(__file__).absolute().parent
SPIDER_STOP_ON_ERROR = True  # spider 在报错时停止（spider、pipeline、middleware）

'''MYSQL'''
# MYSQL_HOST = '127.0.0.1'
# MYSQL_PORT = 3306
# MYSQL_DB = None
# MYSQL_USER = 'root'
# MYSQL_PWD = None
# MYSQL_CONFIG = {}  # 字典形式

'''POSTGRESQL'''
# PG_HOST = '127.0.0.1'
# PG_PORT = 5432
# PG_DB = 'postgres'
# PG_USER = 'postgres'
# PG_PWD = None
# PG_CONFIG = {}  # 字典形式

'''MONGO'''
# MONGO_HOST = '127.0.0.1'
# MONGO_PORT = 27017
# MONGO_USER = None
# MONGO_PWD = None
# MONGO_CONFIG = {}  # 字典形式

'''KAFKA'''
# KAFKA_SERVER = None
# KAFKA_CONFIG = {}  # 字典形式

'''REDIS'''
# REDIS_DB = 0
# REDIS_HOST = '127.0.0.1'
# REDIS_PORT = 6379
# REDIS_PWD = None
# REDIS_CLUSTER_NODES = None  # 如果有集群的情况下，优先集群
# REDIS_MAX_CONNECTIONS = 50  # redis 最大连接数（线程数太大，会连接失败，需要调整）
# REDIS_CONFIG = {}  # redis 连接自定义配置项
# REDIS_POOL_CONFIG = {}  # redis pool 连接自定义配置项

'''请求相关'''
# REQUEST_BORROW = False  # 分发大量任务时，复用请求的一些参数 (分布式时有效，可自定义，默认复用 cookie 同时开启 keep_cookie)
# REQUEST_BORROW_DELETE_WHEN_START = True  # 启动时删除所有 borrow
# REQUEST_THREADS = 16  # 线程数量
# REQUEST_FAILED_SAVE = False  # 分布式时保存失败的请求（重试之后仍然失败的）
# REQUEST_RETRY_FAILED = False  # 分布式时启动重试失败请求
# PERSISTENCE_REQUEST_FILTER = False  # 是否持久化请求过滤（分布式时才有效，否则每次结束都会清除）
# REQUEST_DELAY = 0  # 请求间隔，可以是 [0, 3] 代表 0-3s
# REQUEST_RETRY_TIMES = 3  # 请求失败重试次数
# REQUEST_TIMEOUT = 10  # 请求超时时间，也可以是元组 (connect timeout, read timeout)
# RANDOM_USERAGENT = False  # 随机请求头（默认是 computer，指定则开启下面的选项）
# RANDOM_USERAGENT_TYPE = 'computer'  # UA 类型：电脑（computer 代表电脑内随便选，后面代表指定浏览器 chrome、opera、firefox、ie、safari）手机：mobile
# DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35'
# REQUEST_PROXIES_TUNNEL_URL = None  # 隧道代理 url
# RESPONSE_DOWNLOADER = 'palp.network.downloader_requests.ResponseDownloaderByRequests'  # 请求器，这里默认是 requests
# RESPONSE_DOWNLOADER_PARSER = 'palp.network.response_requests.RequestsResponse'  # 解析器，这里默认是 requests
# # RESPONSE_DOWNLOADER = 'palp.network.downloader_httpx.ResponseDownloaderByHttpx'  # 请求器，这里是 httpx
# # RESPONSE_DOWNLOADER_PARSER = 'palp.network.response_httpx.HttpxResponse'  # 解析器，这里是 httpx


'''PIPELINE'''
# ITEM_THREADS = 5  # item 处理的线程数量，默认 5
# ITEM_FAILED_SAVE = False  # 分布式时保存失败的请求（重试之后仍然失败的）
# ITEM_RETRY_FAILED = False  # 分布式时启动重试失败请求
# PIPELINE_ITEM_BUFFER = 0  # 缓存数量，只有当 item 达到一定数量才会入库，0 为不进行缓存
# PIPELINE_RETRY_TIMES = 3  # 入库失败重试次数

# 下载中间件：请求前的处理
PIPELINE = {
    1: "pipelines.pipeline.Pipeline",
}

'''MIDDLEWARE'''
# 请求中间件
REQUEST_MIDDLEWARE = {
    1: "middlewares.middleware.RequestMiddleware",
}

# spider 中间件
SPIDER_MIDDLEWARE = {
    1: 'middlewares.middleware.SpiderMiddleware',
}

'''过滤器'''
# BLOOMFILTER_BIT = 6
# BLOOMFILTER_HASH_NUMBER = 30
# STRICT_FILTER = False  # 严格去重（加锁，会严重影响抓取效率）
# FILTER_ITEM = False  # item 去重
# FILTER_REQUEST = False  # 请求去重
# FILTERING_MODE = 2  # 去重方式：1 为 set 集合，2 为 bloom 过滤（默认）
# PERSISTENCE_ITEM_FILTER = False  # 是否持久化 item 过滤（分布式时才有效，否则每次结束都会清除）

'''队列'''
# REQUEST_QUEUE_MODE = 3  # 1 为先进先出队列，2 为后进先出队列，3 为优先级队列
# DEFAULT_QUEUE_PRIORITY = 300  # 默认的优先级队列的优先级

'''其它'''
# 预警：Email（from palp import send_email）
# EMAIL_USER = None  # Email 账号
# EMAIL_PWD = None  # Email 授权码

# 预警：DingTalk（from palp import send_dingtalk）
# DING_TALK_SECRET = None  # 加签
# DING_TALK_ACCESS_TOKEN = None  # webhook 链接内的 access_token

# 日志（详见：https://loguru.readthedocs.io/en/latest/）
# LOG_LEVEL = "DEBUG"  # 日志过滤等级
# LOG_SHOW = True  # 是否打印日志
# LOG_SAVE = False  # 是否保存日志
LOG_PATH = BASE_PATH.joinpath('log')  # 日志存放地址
# LOG_ROTATION = '500 MB'  # 日志切割方式（日志官网搜索 rotation）
# LOG_RETENTION = '5 days'  # 日志清理时间（日志官网搜索 retention）
# LOG_COMPRESSION = 'zip'  # 日志压缩方式（gz、bz2、xz、lzma、tar、tar.gz、tar.bz2、tar.xz、zip）
