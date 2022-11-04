"""
    通过 redis 实现心跳功能
"""
import json
import time
import uuid
import datetime
import threading
from loguru import logger
from palp import settings
from palp.conn.conn_redis import RedisLockNoWait, Redis, RedisLock


class ClientHeart:
    def __init__(self, spider):
        """

        :param spider:
        """
        self.spider = spider

        self.beating_time = 4  # 心跳频率
        self.check_time = self.beating_time - 1  # 心跳检查频率
        self.client_name = self.generate_client_name()  # 随机客户端名

    def start(self):
        threading.Thread(target=self.beating, daemon=True).start()

        try:
            self.check_client_beating()
        finally:
            self.close()

    def check_client_beating(self):
        """
        检查各个客户端的心跳，超过 2 次视为停止

        注意：因为不是需要每个都运行，而是同时有一个去运行，所以使用了 RedisLockNoWait
        :return:
        """
        while not self.all_client_is_waiting:

            all_client_is_waiting = True

            with RedisLockNoWait(lock_name=settings.REDIS_KEY_LOCK, block_timeout=10) as lock:
                # 判断是否上锁成功
                if not lock.lock_success:
                    continue

                # 上锁成功则判断客户端运行情况
                for client_name, detail in Redis.conn().hgetall(settings.REDIS_KEY_HEARTBEAT).items():
                    client_name = client_name.decode()
                    detail = json.loads(detail.decode())

                    # 校验 2 次失败则为客户端关闭
                    if int(time.time()) - detail['time'] - self.beating_time > 1:
                        if Redis.conn().sismember(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name):
                            logger.warning(f"该客户端异常关闭：{client_name}")
                            Redis.conn().srem(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name)
                            Redis.conn().hdel(settings.REDIS_KEY_HEARTBEAT, client_name)
                        else:
                            logger.warning(f"该客户端可能异常关闭：{client_name}")
                            Redis.conn().sadd(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name)
                    else:
                        if Redis.conn().sismember(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name):
                            Redis.conn().srem(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name)

                        if detail['waiting'] is False:
                            all_client_is_waiting = False
                        logger.debug(f"心跳正常：{client_name}")

                # 如果所有客户端都无任务，则结束
                if all_client_is_waiting:
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
        while not self.all_client_is_waiting:
            Redis.conn().hset(
                settings.REDIS_KEY_HEARTBEAT,
                self.client_name,
                json.dumps({
                    "time": int(time.time()),
                    "waiting": self.spider.all_parser_is_waiting(),
                }, ensure_ascii=False)
            )
            time.sleep(self.beating_time)

    def close(self):
        """
        清理资源

        :return:
        """
        Redis.conn().hdel(settings.REDIS_KEY_HEARTBEAT, self.client_name)

    @staticmethod
    def stop_all_client():
        """
        发出停止信号，让所有程序停止

        :return:
        """
        Redis.conn().set(settings.REDIS_KEY_STOP, '停止时间：' + str(datetime.datetime.now()))

    @property
    def all_client_is_waiting(self) -> bool:
        """
        判断是否所有客户端都陷入了等待

        :return:
        """
        return bool(Redis.conn().exists(settings.REDIS_KEY_STOP))

    @staticmethod
    def remove_stop_status():
        """
        移除停止信号

        :return:
        """
        while True:
            if not Redis.conn().exists(settings.REDIS_KEY_HEARTBEAT):
                Redis.conn().delete(settings.REDIS_KEY_STOP)
                break

            time.sleep(0.1)

    @staticmethod
    def generate_client_name() -> str:
        """
        生成客户端的名字

        :return:
        """
        while True:
            name = str(uuid.uuid1())
            with RedisLock(lock_name=settings.REDIS_KEY_LOCK, block_timeout=10):
                if Redis.conn().hget(settings.REDIS_KEY_HEARTBEAT, name):
                    continue
                else:
                    Redis.conn().hset(settings.REDIS_KEY_HEARTBEAT, name, json.dumps({
                        "time": int(time.time()),
                        "waiting": False,
                    }, ensure_ascii=False))
                    return name
