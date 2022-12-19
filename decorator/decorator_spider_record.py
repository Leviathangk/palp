"""
    爬虫执行结果汇总记录装饰器

    本身记录的过程是在中间件 RequestRecordMiddleware 中记录，并更新到 spider_record 变量上
    注意：
        这里侧重的爬虫执行结束之后的结果汇总

    爬虫执行完毕后这要做的事
        本地爬虫：无
        分布式爬虫：发送到 redis 最终多端合并
"""
import json
import datetime
from palp import settings


class SpiderRecordDecorator:
    """
        爬虫执行结果汇总记录装饰器
    """

    @staticmethod
    def record(spider):
        """
            进行记录
        """
        from palp.conn import redis_conn

        # 非分布式不上传 redis
        if settings.SPIDER_TYPE == 1:
            return

        # 发送每个 spider 的爬取情况
        redis_conn.hset(settings.REDIS_KEY_RECORD, spider.spider_uuid, json.dumps({
            'request_all': spider.spider_record['all'],
            'request_failed': spider.spider_record['failed'],
            'request_succeed': spider.spider_record['succeed'],
            'stop_time': str(datetime.datetime.now())
        }, ensure_ascii=False))

        # 删除当前 spider 心跳字段
        redis_conn.hdel(settings.REDIS_KEY_HEARTBEAT, spider.spider_uuid)

        # 如果是最后一个心跳，则进行统计记录
        if not redis_conn.exists(settings.REDIS_KEY_HEARTBEAT):
            request_all = 0
            request_failed = 0
            request_succeed = 0

            # 统计
            for spider_uuid, spider_detail in redis_conn.hgetall(settings.REDIS_KEY_RECORD).items():
                spider_detail = json.loads(spider_detail.decode())

                request_all += spider_detail['request_all']
                request_failed += spider_detail['request_failed']
                request_succeed += spider_detail['request_succeed']

            # 发送最后的统计结果
            redis_conn.set(settings.REDIS_KEY_STOP, json.dumps({
                'request_all': request_all,
                'request_failed': request_failed,
                'request_succeed': request_succeed,
                'stop_time': str(datetime.datetime.now())
            }, ensure_ascii=False))

    def __call__(self, func):
        def _wrapper(*args, **kwargs):
            # 先执行函数
            try:
                func(*args, **kwargs)
            finally:
                # 获取 spider
                spider = args[0]

                # 统计数据
                self.record(spider=spider)

        return _wrapper
