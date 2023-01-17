"""
    单次执行装饰器：执行 request_record、spider_end（分布式时只执行一次）

    执行结果记录：
        本身记录的过程是在中间件 RequestRecordMiddleware 中记录，并更新到 spider_record 变量上
        注意：
            这里侧重的爬虫执行结束之后的结果汇总

        爬虫执行完毕后这要做的事
            本地爬虫：无
            分布式爬虫：发送到 redis 最终多端合并
"""
import json
import datetime
import traceback
from palp import settings
from quickdb import RedisLock
from palp.controller import SpiderController


class SpiderOnceDecorator:
    """
        爬虫单次执行 request_record、spider_end
    """

    @classmethod
    def run_once(cls, spider):
        """
        记录请求量

        :param spider:
        :return:
        """
        from palp.conn import redis_conn

        # 非分布式不上传 redis
        if settings.SPIDER_TYPE == 1:
            cls.run_request_record(spider=spider, record=spider.spider_record)
            cls.run_spider_end(spider=spider)
            return

        # 发送每个 spider 的爬取情况
        redis_conn.hset(settings.REDIS_KEY_RECORD, spider.spider_uuid, json.dumps({
            'all': spider.spider_record['all'],
            'failed': spider.spider_record['failed'],
            'succeed': spider.spider_record['succeed'],
            'stop_time': str(datetime.datetime.now())
        }, ensure_ascii=False))

        # 保证 send_record 只执行一次
        is_end = False
        with RedisLock(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK + 'Record'):
            # 删除当前 spider 心跳字段
            redis_conn.hdel(settings.REDIS_KEY_HEARTBEAT, spider.spider_uuid)

            # 如果是最后一个心跳，则进行统计记录
            if not redis_conn.exists(settings.REDIS_KEY_HEARTBEAT):
                is_end = True

        # 统计所有机器的结果
        if is_end:
            request_all = 0
            request_failed = 0
            request_succeed = 0

            # 统计
            for spider_uuid, spider_detail in redis_conn.hgetall(settings.REDIS_KEY_RECORD).items():
                spider_detail = json.loads(spider_detail.decode())

                request_all += spider_detail['all']
                request_failed += spider_detail['failed']
                request_succeed += spider_detail['succeed']

            # 给请求中间件发送统计结果
            cls.run_request_record(spider=spider, record={
                'all': request_all,
                'failed': request_failed,
                'succeed': request_succeed,
            })

            # 执行 spider_end
            cls.run_spider_end(spider=spider)

    @staticmethod
    def run_request_record(spider, record: dict):
        """
        调用请求中间件的 request_record 函数发送记录

        record 目前有 3 个字段：all、failed、succeed
        :return:
        """
        for middleware in SpiderController.REQUEST_MIDDLEWARE:
            try:
                middleware.request_record(spider, record)
            except:
                traceback.print_exc()

    @staticmethod
    def run_spider_end(spider):
        """
        执行 spider_end

        :param spider:
        :return:
        """
        for middleware in spider.__class__.SPIDER_MIDDLEWARE:
            try:
                middleware.spider_end(spider)
            except:
                traceback.print_exc()

    def __call__(self, func):
        def _wrapper(*args, **kwargs):
            # 先执行函数
            try:
                func(*args, **kwargs)
            finally:
                # 获取 spider
                spider = args[0]

                # 统计数据
                self.run_once(spider=spider)

        return _wrapper
