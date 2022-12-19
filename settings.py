"""
    配置
        配置优先级 spider > spider setting > palp setting
        三者的配置是覆盖的关系
"""
from pathlib import Path

BASE_PATH = Path(__file__).absolute().parent
SPIDER_TYPE = 1  # 爬虫的类型（1 airspider 2 分布式 spider）（非用户设置）
SPIDER_STOP_ON_ERROR = False  # spider 在报错时停止（spider、pipeline、middleware）

'''MYSQL'''
MYSQL_HOST = None
MYSQL_PORT = None
MYSQL_DB = None
MYSQL_USER = None
MYSQL_PWD = None
MYSQL_CONFIG = {}  # 字典形式

'''POSTGRESQL'''
PG_HOST = None
PG_PORT = None
PG_DB = None
PG_USER = None
PG_PWD = None
PG_CONFIG = {}  # 字典形式

'''MONGO'''
MONGO_HOST = None
MONGO_PORT = None
MONGO_USER = None
MONGO_PWD = None
MONGO_CONFIG = {}  # 字典形式

'''KAFKA'''
KAFKA_SERVER = None
KAFKA_CONFIG = {}  # 字典形式

'''REDIS'''
REDIS_DB = 0
REDIS_HOST = None
REDIS_PORT = None
REDIS_PWD = None
REDIS_CLUSTER_NODES = None  # 如果有集群的情况下，优先集群
REDIS_MAX_CONNECTIONS = 5  # redis 最大连接数
REDIS_CONFIG = {}  # redis 连接自定义配置项
REDIS_POOL_CONFIG = {}  # redis pool 连接自定义配置项

# 分布式时的 REDIS KEY
REDIS_KEY_MASTER = '{redis_key}:master'  # redis master（分布式时）(str)
REDIS_KEY_LOCK = '{redis_key}:lock'  # redis 锁(str)
REDIS_KEY_STOP = '{redis_key}:stop'  # 停止所有机器运行（分布式时）(str)
REDIS_KEY_QUEUE_REQUEST = '{redis_key}:request'  # request 队列（list、zset）
REDIS_KEY_QUEUE_BAD_REQUEST = '{redis_key}:requestFailed'  # request 失败队列（set）
REDIS_KEY_QUEUE_FILTER_REQUEST = '{redis_key}:filter:request'  # request 过滤队列（set、bloom）
REDIS_KEY_QUEUE_ITEM = '{redis_key}:item'  # item 队列（list）
REDIS_KEY_QUEUE_BAD_ITEM = '{redis_key}:itemFailed'  # item 失败队列（set）
REDIS_KEY_QUEUE_FILTER_ITEM = '{redis_key}:filter:item'  # item 过滤队列（set、bloom）
REDIS_KEY_HEARTBEAT = '{redis_key}:heartbeat'  # 机器的心跳（hash）
REDIS_KEY_HEARTBEAT_FAILED = '{redis_key}:heartbeat_failed'  # 校验失败的机器（set）

'''请求相关'''
REQUEST_THREADS = 16  # 线程数量
REQUEST_FAILED_SAVE = False  # 分布式时保存失败的请求（重试之后仍然失败的）
REQUEST_RETRY_FAILED = False  # 分布式时启动重试失败请求
PERSISTENCE_REQUEST_FILTER = False  # 是否持久化请求过滤（分布式时才有效，否则每次结束都会清除）
REQUEST_DELAY = 0  # 请求间隔，可以是 [0, 3] 代表 0-3s
REQUEST_RETRY_TIMES = 3  # 请求失败重试次数
REQUEST_TIMEOUT = 10  # 请求超时时间，也可以是元组 (connect timeout, read timeout)
RANDOM_USERAGENT = False  # 随机请求头（默认是 computer，指定则开启下面的选项）
RANDOM_USERAGENT_TYPE = 'computer'  # UA 类型：电脑（computer 代表电脑内随便选，后面代表指定浏览器 chrome、opera、firefox、ie、safari）手机：mobile
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35'
REQUEST_PROXIES_TUNNEL_URL = None  # 隧道代理 url
RESPONSE_DOWNLOADER = 'palp.network.downloader_requests.ResponseDownloaderByRequests'  # 请求器，这里默认是 requests
RESPONSE_DOWNLOADER_PARSER = 'palp.network.response_requests.RequestsResponse'  # 解析器，这里默认是 requests
# RESPONSE_DOWNLOADER = 'palp.network.downloader_httpx.ResponseDownloaderByHttpx'  # 请求器，这里是 httpx
# RESPONSE_DOWNLOADER_PARSER = 'palp.network.response_httpx.HttpxResponse'  # 解析器，这里是 httpx


'''PIPELINE'''
ITEM_THREADS = 5  # item 处理的线程数量，默认 5
ITEM_FAILED_SAVE = False  # 分布式时保存失败的请求（重试之后仍然失败的）
ITEM_RETRY_FAILED = False  # 分布式时启动重试失败请求
PIPELINE_ITEM_BUFFER = 0  # 缓存数量，只有当 item 达到一定数量才会入库，0 为不进行缓存
PIPELINE_RETRY_TIMES = 3  # 入库失败重试次数

# 下载中间件：请求前的处理
PIPELINE = {
    1: "palp.pipeline.pipeline.Pipeline",
}

PALP_PIPELINE = {
    'min': {
        'ITEM_FILTER_PIPELINE': 1
    },
    'max': {
        1: ['ITEM_FAILED_SAVE', 'palp.pipeline.pipeline_recycle.RedisRecyclePipeline']
    }
}

'''MIDDLEWARE'''
# 请求中间件
REQUEST_MIDDLEWARE = {
    1: "palp.middleware.middleware_request.RequestMiddleware",
}

# palp 必须的请求中间件，非用户定义（min、max 代表 REQUEST_MIDDLEWARE 最小最大索引）
PALP_REQUEST_MIDDLEWARE = {
    'min': {
        1: "palp.middleware.middleware_request_check.RequestCheckMiddleware",  # 请求检查
        'REQUEST_FILTER_MIDDLEWARE': 2,  # 请求过滤（反着来代表占用，程序内也要传参，就会转化）
        3: 'palp.middleware.middleware_request_record.RequestsRecordMiddleware'  # 记录请求
    },
    'max': {
        1: ['REQUEST_FAILED_SAVE', 'palp.middleware.middleware_request_recycle.RequestRecycleMiddleware']  # 列表代表判断
    }
}

# spider 中间件
SPIDER_MIDDLEWARE = {
    1: 'palp.middleware.middleware_spider.SpiderMiddleware',
}

# palp 必须的请求中间件，非用户定义
PALP_SPIDER_MIDDLEWARE = {
    'min': {
    },
    'max': {
        1: 'palp.middleware.middleware_spider_recycle.SpiderRecycleMiddleware',  # 资源回收
        2: 'palp.middleware.middleware_request_record.RequestsRecordMiddleware'  # 记录请求
    }
}

'''过滤器'''
BLOOMFILTER_BIT = 6
BLOOMFILTER_HASH_NUMBER = 30
STRICT_FILTER = False  # 严格去重（加锁，会严重影响抓取效率）
FILTER_ITEM = False  # item 去重
FILTER_REQUEST = False  # 请求去重
FILTERING_MODE = 2  # 去重方式：1 为 set 集合，2 为 bloom 过滤（默认）
PERSISTENCE_ITEM_FILTER = False  # 是否持久化 item 过滤（分布式时才有效，否则每次结束都会清除）

# item 过滤中间件（1、本地，2、云端分布式）
ITEM_FILTER_PIPELINE = {
    1: {
        1: 'palp.pipeline.pipeline_filter.SetFilterPipeline',  # 本地：set 过滤
        2: 'palp.pipeline.pipeline_filter.BloomFilterPipeline',  # 本地：布隆过滤
    },
    2: {
        1: 'palp.pipeline.pipeline_filter.RedisSetFilterPipeline',  # redis：set 过滤
        2: 'palp.pipeline.pipeline_filter.RedisBloomFilterPipeline'  # redis：布隆过滤
    }
}

# 请求过滤中间件（1、本地，2、云端分布式）
REQUEST_FILTER_MIDDLEWARE = {
    1: {
        1: 'palp.middleware.middleware_request_filter.SetFilterMiddleware',  # 本地：set 过滤
        2: 'palp.middleware.middleware_request_filter.BloomFilterMiddleware',  # 本地：布隆过滤
    },
    2: {
        1: 'palp.middleware.middleware_request_filter.RedisSetFilterMiddleware',  # redis：set 过滤
        2: 'palp.middleware.middleware_request_filter.RedisBloomFilterMiddleware'  # redis：布隆过滤
    }
}

'''队列'''
REQUEST_QUEUE_MODE = 3  # 1 为先进先出队列，2 为后进先出队列，3 为优先级队列
ITEM_QUEUE_MODE = 1  # 1 为先进先出队列，2 为后进先出队列（未使用）
DEFAULT_QUEUE_PRIORITY = 300  # 默认的优先级队列的优先级
REQUEST_QUEUE = {
    1: {
        1: 'palp.sequence.sequence_memory.FIFOMemorySequence',  # 本地：先进先出队列
        2: 'palp.sequence.sequence_memory.LIFOMemorySequence',  # 本地：后进先出队列
        3: 'palp.sequence.sequence_memory.PriorityMemorySequence',  # 本地：优先级队列（通过 request 的 level 指定 越小越高）
    },
    2: {
        1: 'palp.sequence.sequence_redis_request.FIFORequestRedisSequence',  # redis：先进先出队列
        2: 'palp.sequence.sequence_redis_request.LIFORequestRedisSequence',  # redis：后进先出队列
        3: 'palp.sequence.sequence_redis_request.PriorityRequestRedisSequence',  # redis：优先级队列（通过 request 的 level 指定）
    }
}
ITEM_QUEUE = {
    1: {
        1: 'palp.sequence.sequence_memory.FIFOMemorySequence',  # 本地：先进先出队列
        2: 'palp.sequence.sequence_memory.LIFOMemorySequence',  # 本地：后进先出队列
    },
    2: {
        1: 'palp.sequence.sequence_redis_item.FIFOItemRedisSequence',  # redis：先进先出队列
        2: 'palp.sequence.sequence_redis_item.LIFOItemRedisSequence',  # redis：后进先出队列
    }
}

'''其它'''
# 预警：Email（from palp import send_email）
EMAIL_USER = None  # Email 账号
EMAIL_PWD = None  # Email 授权码

# 预警：DingTalk（from palp import send_dingtalk）
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
