"""
    配置
        配置优先级 spider > spider setting > palp setting
        三者的配置是覆盖的关系
"""
from pathlib import Path

SPIDER_TYPE = 1  # 爬虫的类型（1 airspider 2 分布式 spider）（非用户设置）
BASE_PATH = Path(__file__).absolute().parent

# REDIS
REDIS_DB = 0
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PWD = None
REDIS_CLUSTER_NODES = None  # 如果有集群的情况下，优先集群
REDIS_MAX_CONNECTIONS = 5  # redis 最大连接数
REDIS_CONFIG = {}  # redis 连接自定义配置项
REDIS_POOL_CONFIG = {}  # redis pool 连接自定义配置项

# 分布式时的 REDIS KEY
REDIS_KEY_MASTER = '{redis_key}:master'  # redis master（分布式时）
REDIS_KEY_LOCK = '{redis_key}:lock'  # redis 锁
REDIS_KEY_STOP = '{redis_key}:stop'  # 停止所有机器运行（分布式时）
REDIS_KEY_QUEUE_REQUEST = '{redis_key}:request'  # request 队列
REDIS_KEY_QUEUE_FILTER_REQUEST = '{redis_key}:filter:request'  # request 过滤队列
REDIS_KEY_QUEUE_ITEM = '{redis_key}:item'  # item 队列
REDIS_KEY_QUEUE_FILTER_ITEM = '{redis_key}:filter:item'  # item 过滤队列
REDIS_KEY_HEARTBEAT = '{redis_key}:heartbeat'  # 机器的心跳（hash）
REDIS_KEY_HEARTBEAT_FAILED = '{redis_key}:heartbeat_failed'  # 校验失败的机器

'''请求相关'''
PERSISTENCE_REQUEST_FILTER = False  # 是否持久化请求过滤（分布式时才有效，否则每次结束都会清除）
REQUEST_FILTER = False  # 去重请求，开启了请求时的 filter_repeat 才有用
REQUEST_RETRY_TIMES = 3  # 请求失败重试次数
REQUEST_DELAY = 0  # 请求间隔
REQUEST_TIMEOUT = 10  # 请求超时时间，也可以是元组 (connect timeout, read timeout)
RANDOM_USERAGENT = True  # 如果请求头不含 UA 将会设置，但是自己设置了 UA 则不会设置（默认是 computer，指定则开启下面的选项）
RANDOM_USERAGENT_TYPE = 'computer'  # UA 类型：电脑（computer 代表电脑内随便选，后面代表指定浏览器 chrome、opera、firefox、ie、safari）手机：mobile
REQUEST_PROXIES_TUNNEL_URL = None  # 隧道代理 url

# 请求中间件：处理请求中的各种情况
REQUEST_MIDDLEWARE = [
    "palp.middleware.middleware_request_base.BaseRequestMiddleware",
]

# 请求队列
REQUEST_MODE = 1  # 1 为先进先出队列，2 为后进先出队列，3 为优先级队列
REQUEST_QUEUE = {
    1: {
        1: 'palp.sequence.sequence_memory.FIFOSequence',  # 本地：先进先出队列
        2: 'palp.sequence.sequence_memory.LIFOSequence',  # 本地：后进先出队列
        3: 'palp.sequence.sequence_memory.PrioritySequence',  # 本地：优先级队列（通过 request 的 level 指定，默认 level 10，越小越高）
    },
    2: {
        1: 'palp.sequence.sequence_redis_request.FIFOSequence',  # redis：先进先出队列
        2: 'palp.sequence.sequence_redis_request.LIFOSequence',  # redis：后进先出队列
        3: 'palp.sequence.sequence_redis_request.PrioritySequence',  # redis：优先级队列（通过 request 的 level 指定，默认 level 10，越小越高）
    }
}

# 下载中间件：请求前的处理
PIPELINE_ITEM_BUFFER = 0  # 缓存数量，只有当 item 达到一定数量才会入库，0 为不进行缓存
PIPELINE_RETRY_TIMES = 3  # 入库失败重试次数
PIPELINE = [
    "palp.pipeline.pipeline_base.BasePipeline",
]

'''过滤去重'''
BLOOMFILTER_BIT = 6
BLOOMFILTER_HASH_NUMBER = 30
FILTERING_MODE = 2  # 去重方式：1 为 set 集合，2 为 bloom 过滤
ITEM_FILTER = False  # 是否去重 item 默认不去重
PERSISTENCE_ITEM_FILTER = False  # 是否持久化 item 过滤（分布式时才有效，否则每次结束都会清除）

# item 过滤中间件（1、本地，2、云端分布式）
ITEM_FILTER_PIPELINE = {
    1: {
        1: 'palp.pipeline.pipeline_item_filter.ItemMemoryFilterPipeline',  # 本地：set 过滤
        2: 'palp.pipeline.pipeline_item_filter.ItemBloomFilterPipeline',  # 本地：布隆过滤
    },
    2: {
        1: 'palp.pipeline.pipeline_item_filter.ItemRedisFilterPipeline',  # redis：set 过滤
        2: 'palp.pipeline.pipeline_item_filter.ItemRedisBloomFilterPipeline'  # redis：布隆过滤
    }
}

# 请求过滤中间件（1、本地，2、云端分布式）
REQUEST_FILTER_MIDDLEWARE = {
    1: {
        1: 'palp.middleware.middleware_request_filter.RequestMemoryFilterMiddleware',  # 本地：set 过滤
        2: 'palp.middleware.middleware_request_filter.RequestBloomFilterMiddleware',  # 本地：布隆过滤
    },
    2: {
        1: 'palp.middleware.middleware_request_filter.RequestRedisFilterMiddleware',  # redis：set 过滤
        2: 'palp.middleware.middleware_request_filter.RequestRedisBloomFilterMiddleware'  # redis：布隆过滤
    }
}

# spider 中间件
SPIDER_MIDDLEWARE = [
    'palp.middleware.middleware_spider_base.BaseSpiderMiddleware',
]

# 爬虫本身配置
SPIDER_THREAD_COUNT = 16  # spider 默认的线程数量

# 预警：Email
EMAIL_USER = None  # Email 账号
EMAIL_PWD = None  # Email 授权码
EMAIL_RECEIVER = []  # Email 接收者列表

# 预警：DingTalk
DING_TALK_AT_MOBILES = []  # @ 手机号
DING_TALK_AT_USER_IDS = []  # @ user_id
DING_TALK_AT_ALL = False  # @ 所有人
DING_TALK_SECRET = None  # 加签
DING_TALK_ACCESS_TOKEN = None  # webhook 链接内的 access_token

# 日志（详见：https://loguru.readthedocs.io/en/latest/）
LOG_LEVEL = "DEBUG"  # 日志过滤等级
LOG_SHOW = True  # 是否打印日志
LOG_SAVE = False  # 是否保存日志
LOG_PATH = BASE_PATH.joinpath('log')  # 日志存放地址
LOG_ROTATION = '5 MB'  # 日志切割方式，这里是 5m
LOG_RETENTION = '5 days'  # 日志清理时间
LOG_COMPRESSION = 'zip'  # 日志压缩方式（gz、bz2、xz、lzma、tar、tar.gz、tar.bz2、tar.xz、zip）

# 导入 用户的 spider 设置
try:
    from settings import *
except:
    pass
