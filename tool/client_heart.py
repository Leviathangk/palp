"""
    通过 redis 实现心跳功能

    master 异常会把自己设置为 slave
    slave 检测到 master 死机会把自己设置为 master
"""
import json
import time
import uuid
import datetime
import threading
from loguru import logger
from palp import settings
from quickdb import RedisLockNoWait, RedisLock


class ClientHeart:
    def __init__(self, spider):
        """

        :param spider:
        """
        self.spider = spider

        self.stop = False  # 停止标志（用于异常时）
        self.beating_time = 4  # 心跳频率
        self.check_time = self.beating_time - 1  # 心跳检查频率
        self.client_name = self.generate_client_name()  # 随机客户端名

    def start(self):
        beating = threading.Thread(target=self.beating, daemon=True)
        beating.start()

        try:
            self.check_client_beating()
        except Exception as e:
            self.stop = True
            self.spider.spider_master = False
            logger.exception(e)
        finally:
            self.close(beating)

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

                # 上锁成功则判断客户端运行情况
                for client_name, detail in redis_conn.hgetall(settings.REDIS_KEY_HEARTBEAT).items():
                    client_name = client_name.decode()
                    detail = json.loads(detail.decode())

                    # 校验 2 次失败则为客户端关闭
                    if int(time.time()) - detail['time'] - self.beating_time > 1:
                        if redis_conn.sismember(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name):
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
                                master_detail['name'] = self.client_name
                                redis_conn.set(settings.REDIS_KEY_MASTER, json.dumps(master_detail, ensure_ascii=False))
                    else:
                        if redis_conn.sismember(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name):
                            redis_conn.srem(settings.REDIS_KEY_HEARTBEAT_FAILED, client_name)

                        if detail['waiting'] is False:
                            all_client_is_waiting = False
                        logger.debug(f"心跳正常：{client_name}")

                # 如果所有客户端都无任务，则结束
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

        while not self.stop and not self.all_client_is_waiting:
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
                self.client_name,
                json.dumps(heart, ensure_ascii=False)
            )
            time.sleep(self.beating_time)

    def close(self, beating: threading.Thread):
        """
        清理资源

        :return:
        """
        from palp.conn import redis_conn

        while True:
            if not beating.is_alive():
                redis_conn.hdel(settings.REDIS_KEY_HEARTBEAT, self.client_name)
                break

    @staticmethod
    def master_distribute_thread_is_done() -> bool:
        """
        判断 master 有没有把任务分发完毕

        注意：master 死机后 slave 接管 master 会直接设置为 False
        :return:
        """
        from palp.conn import redis_conn

        master_detail = json.loads(redis_conn.get(settings.REDIS_KEY_MASTER).decode())
        res = redis_conn.hget(settings.REDIS_KEY_HEARTBEAT, master_detail['name']).decode()

        return json.loads(res)['distribute_done']

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

    @staticmethod
    def remove_stop_status():
        """
        移除停止信号

        :return:
        """
        from palp.conn import redis_conn

        while True:
            if not redis_conn.exists(settings.REDIS_KEY_HEARTBEAT):
                redis_conn.delete(settings.REDIS_KEY_STOP)
                break

            time.sleep(0.1)

    def generate_client_name(self) -> str:
        """
        生成客户端的名字

        :return:
        """
        from palp.conn import redis_conn

        while True:
            name = str(uuid.uuid1())
            with RedisLock(conn=redis_conn, lock_name=settings.REDIS_KEY_LOCK + 'GenerateHeart', block_timeout=10):
                if redis_conn.hget(settings.REDIS_KEY_HEARTBEAT, name):
                    continue
                else:

                    # master 重新起名字
                    if self.spider.spider_master:
                        master_detail = json.loads(redis_conn.get(settings.REDIS_KEY_MASTER).decode())
                        master_detail['name'] = name
                        redis_conn.set(settings.REDIS_KEY_MASTER, json.dumps(master_detail, ensure_ascii=False))

                    # 发送起始心跳
                    redis_conn.hset(settings.REDIS_KEY_HEARTBEAT, name, json.dumps({
                        "time": int(time.time()),
                        "waiting": False,  # 是否所有线程没事干
                        'distribute_done': False,  # 任务分发是否结束
                    }, ensure_ascii=False))

                    return name
