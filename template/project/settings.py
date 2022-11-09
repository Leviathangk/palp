"""
    配置
        配置优先级 spider > spider setting > palp setting
        三者的配置是覆盖的关系

    注意：
        Spider 可设置独有的配置为字段 spider_settings （可以是字典，也可以是 from xxx import settings）
"""
from pathlib import Path

BASE_PATH = Path(__file__).absolute().parent

'''MYSQL'''
# MYSQL_HOST = None
# MYSQL_PORT = None
# MYSQL_DB = None
# MYSQL_USER = None
# MYSQL_PWD = None
# MYSQL_CONFIG = {}  # 字典形式

'''POSTGRESQL'''
# PG_HOST = None
# PG_PORT = None
# PG_DB = None
# PG_USER = None
# PG_PWD = None
# PG_CONFIG = {}  # 字典形式

'''REDIS'''
# REDIS_DB = 0
# REDIS_HOST = '127.0.0.1'
# REDIS_PORT = 6379
# REDIS_PWD = None
# REDIS_CLUSTER_NODES = None  # 如果有集群的情况下，优先集群
# REDIS_MAX_CONNECTIONS = 5  # redis 最大连接数
# REDIS_CONFIG = {}  # redis 连接自定义配置项
# REDIS_POOL_CONFIG = {}  # redis pool 连接自定义配置项

'''请求相关'''
# REQUEST_FILTER = False  # 去重请求，开启了，请求时的 filter_repeat 才有用（不然分布式时使用分布式锁，会极大的降低速度）
# REQUEST_DELAY = 0  # 请求间隔
# REQUEST_RETRY_TIMES = 3  # 请求失败重试次数
# REQUEST_TIMEOUT = 10  # 请求超时时间，也可以是元组 (connect timeout, read timeout)
# RANDOM_USERAGENT = False  # 如果请求头不含 UA 将会设置，但是自己设置了 UA 则不会设置（默认是 computer，指定则开启下面的选项）
# RANDOM_USERAGENT_TYPE = 'computer'  # UA 类型：电脑（computer 代表电脑内随便选，后面代表指定浏览器 chrome、opera、firefox、ie、safari）手机：mobile
# DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35'
# REQUEST_PROXIES_TUNNEL_URL = None  # 隧道代理 url
# PERSISTENCE_REQUEST_FILTER = False  # 是否持久化请求过滤（分布式时才有效，否则每次结束都会清除）

# 请求中间件：处理请求中的各种情况
REQUEST_MIDDLEWARE = [
    "middlewares.middleware.RequestMiddleware",
]

# 请求队列
# REQUEST_MODE = 1  # 1 为先进先出队列，2 为后进先出队列，3 为优先级队列

'''item'''
# 下载中间件：请求前的处理
# PIPELINE_ITEM_BUFFER = 0  # 缓存数量，只有当 item 达到一定数量才会入库，0 为不进行缓存
# PIPELINE_RETRY_TIMES = 3  # 入库失败重试次数
PIPELINE = [
    "pipelines.pipeline.Pipeline",
]

# 过滤去重
# BLOOMFILTER_BIT = 6
# BLOOMFILTER_HASH_NUMBER = 30
# ITEM_FILTER = False  # 是否去重 item 默认不去重
# PERSISTENCE_ITEM_FILTER = False  # 是否持久化 item 过滤（分布式时才有效，否则每次结束都会清除）

'''other'''
# FILTERING_MODE = 2  # 去重方式：1 为 set 集合，2 为 bloom 过滤（默认）

# spider 中间件
SPIDER_MIDDLEWARE = [
    'middlewares.middleware.SpiderMiddleware',
]

# 爬虫本身配置
# SPIDER_THREAD_COUNT = 16  # spider 默认的线程数量

# 预警：Email
# EMAIL_USER = None  # Email 账号
# EMAIL_PWD = None  # Email 授权码
# EMAIL_RECEIVER = []  # Email 接收者列表

# 预警：DingTalk
# DING_TALK_AT_MOBILES = []  # @ 手机号
# DING_TALK_AT_USER_IDS = []  # @ user_id
# DING_TALK_AT_ALL = False  # @ 所有人
# DING_TALK_SECRET = None  # 加签
# DING_TALK_ACCESS_TOKEN = None  # webhook 链接内的 access_token

# 日志（详见：https://loguru.readthedocs.io/en/latest/）
# LOG_LEVEL = "DEBUG"  # 日志过滤等级
# LOG_SHOW = True  # 是否打印日志
# LOG_SAVE = False  # 是否保存日志
LOG_PATH = BASE_PATH.joinpath('log')  # 日志存放地址
# LOG_ROTATION = '5 MB'  # 日志切割方式，这里是 5m
# LOG_RETENTION = '5 days'  # 日志清理时间
# LOG_COMPRESSION = 'zip'  # 日志压缩方式（gz、bz2、xz、lzma、tar、tar.gz、tar.bz2、tar.xz、zip）

# 导入 用户的 spider 设置
try:
    from settings import *
except:
    pass
