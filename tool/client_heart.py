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

            with RedisLockNoWait(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK + 'CheckHeart',
                                 block_timeout=20) as lock:
                # 判断是否上锁成功
                if not lock.lock_success:
                    continue

                # 获取失败的客户端
                failed_client = [i.decode() for i in redis_conn.smembers(settings.REDIS_KEY_HEARTBEAT_FAILED)]

                # 上锁成功则判断客户端运行情况
                now_time = time.time()
                all_distribute_done = True  # 是否任务分发完毕（只有 master 会分发）
                all_client_is_waiting = True  # 是否所有客户端都无任务处理
                all_item_controller_done = True  # 是否 item 消费完毕

                heartbeat = redis_conn.hgetall(settings.REDIS_KEY_HEARTBEAT)
                for client_name, detail in heartbeat.items():
                    client_name = client_name.decode()
                    detail = json.loads(detail.decode())

                    # 校验 2 次失败则为客户端关闭（当前时间-心跳时间-心跳频率 > 心跳频率）
                    if now_time - detail['time'] - self.beating_time > self.beating_time:
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

                        # 判断各项执行状况
                        if detail['waiting'] is False:
                            all_client_is_waiting = False
                        if detail['distribute_done'] is False:
                            all_distribute_done = False
                        if detail['item_done'] is False:
                            all_item_controller_done = False
                        logger.debug(f"心跳正常：{client_name}")

                # 如果所有客户端都无任务进行，并且任务分发完毕，则结束
                if heartbeat and all_client_is_waiting and all_distribute_done and all_item_controller_done:
                    logger.debug("所有客户端都已挂起，即将停止")
                    self.stop_all_client()
                    break

                time.sleep(self.check_time)

            time.sleep(0.5)  # 避免访问频繁

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
                "waiting": self.spider.all_spider_controller_is_waiting(),  # 任务处理完毕
                'distribute_done': self.spider.all_distribute_thread_is_done(),  # 任务分发完毕
                'item_done': self.spider.all_item_controller_done()  # item 消费完毕
            }

            # 设置 redis 心跳
            redis_conn.hset(
                settings.REDIS_KEY_HEARTBEAT,
                self.spider.spider_uuid,
                json.dumps(heart, ensure_ascii=False)
            )
            time.sleep(self.beating_time)

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
