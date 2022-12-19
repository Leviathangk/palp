"""
    通过 redis 实现心跳功能

    master 异常会把自己设置为 slave
    slave 检测到 master 死机会把自己设置为 master
"""
import json
import time
import datetime
import threading
from loguru import logger
from palp import settings
from quickdb import RedisLockNoWait


class ClientHeart:
    def __init__(self, spider):
        """

        :param spider:
        """
        self.spider = spider
        self.beating_time = 4  # 心跳频率
        self.check_time = self.beating_time - 1  # 心跳检查频率

    def start(self):
        beating = threading.Thread(target=self.beating, daemon=True)
        beating.start()

        try:
            self.check_client_beating()
        except Exception as e:
            self.spider.spider_master = False
            logger.exception(e)

    def check_client_beating(self):
        """
        检查各个客户端的心跳，超过 2 次视为停止

        注意：因为不是需要每个都运行，而是同时有一个去运行，所以使用了 RedisLockNoWait
        :return:
        """
        from palp.conn import redis_conn

        while not self.all_client_is_waiting:

            all_client_is_waiting = True

            with RedisLockNoWait(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK + 'CheckHeart',
                                 block_timeout=20) as lock:
                # 判断是否上锁成功
                if not lock.lock_success:
                    continue

                # 获取失败的客户端
                failed_client = [i.decode() for i in redis_conn.smembers(settings.REDIS_KEY_HEARTBEAT_FAILED)]

                # 上锁成功则判断客户端运行情况
                for client_name, detail in redis_conn.hgetall(settings.REDIS_KEY_HEARTBEAT).items():
                    client_name = client_name.decode()
                    detail = json.loads(detail.decode())

                    # 校验 2 次失败则为客户端关闭
                    if int(time.time()) - detail['time'] - self.beating_time > 1:
                        if client_name in failed_client:
                            logger.warning(f"该客户端异常关闭：{client_name}")
                            redis_conn.srem(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name)
                            redis_conn.hdel(settings.REDIS_KEY_HEARTBEAT, client_name)
                        else:
                            logger.warning(f"该客户端可能异常关闭：{client_name}")
                            redis_conn.sadd(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name)

                            # 检查是否是 master 死机，是的话自己成为 master
                            master_detail = json.loads(redis_conn.get(settings.REDIS_KEY_MASTER).decode())

                            if master_detail and master_detail['name'] == client_name:
                                self.spider.spider_master = True
                                master_detail['name'] = self.spider.spider_uuid
                                redis_conn.set(settings.REDIS_KEY_MASTER, json.dumps(master_detail, ensure_ascii=False))
                    else:
                        if client_name in failed_client:
                            redis_conn.srem(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name)

                        if detail['waiting'] is False:
                            all_client_is_waiting = False
                        logger.debug(f"心跳正常：{client_name}")

                # 如果所有客户端都无任务进行，并且任务分发完毕，则结束
                if all_client_is_waiting and self.master_distribute_thread_is_done():
                    logger.debug("所有客户端都已挂起，即将停止")
                    self.stop_all_client()
                    break

                time.sleep(self.check_time)

            time.sleep(1)  # 避免访问频繁

    def beating(self):
        """
        保持心跳

        :return:
        """
        from palp.conn import redis_conn

        while True:
            # 检测是否分发完毕
            heart = {
                "time": int(time.time()),
                "waiting": self.spider.all_spider_controller_is_waiting(),
            }
            if self.spider.spider_master:
                heart.update({'distribute_done': self.spider.all_distribute_thread_is_done()})
            else:
                heart.update({'distribute_done': False})

            # 设置 redis 心跳
            redis_conn.hset(
                settings.REDIS_KEY_HEARTBEAT,
                self.spider.spider_uuid,
                json.dumps(heart, ensure_ascii=False)
            )
            time.sleep(self.beating_time)

    @staticmethod
    def master_distribute_thread_is_done() -> bool:
        """
        判断 master 有没有把任务分发完毕

        注意：master 死机后 slave 接管 master 会直接设置为 False
        :return:
        """
        from palp.conn import redis_conn

        master_detail = json.loads(redis_conn.get(settings.REDIS_KEY_MASTER).decode())
        res = redis_conn.hget(settings.REDIS_KEY_HEARTBEAT, master_detail['name'])
        if res:
            res = res.decode()  # 一定要判断，不然可能产生时间差，master 还没有心跳，但是已经开始检测心跳

            return json.loads(res)['distribute_done']

        return False

    @staticmethod
    def stop_all_client():
        """
        发出停止信号，让所有程序停止

        :return:
        """
        from palp.conn import redis_conn

        redis_conn.set(settings.REDIS_KEY_STOP, str(datetime.datetime.now()))

    @property
    def all_client_is_waiting(self) -> bool:
        """
        判断是否所有客户端都陷入了等待

        :return:
        """
        from palp.conn import redis_conn

        return bool(redis_conn.exists(settings.REDIS_KEY_STOP))
