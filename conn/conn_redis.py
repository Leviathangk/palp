"""
    redis 连接
    redis 锁

    RedisLock：所有使用该锁的都会等待锁，直到获取并执行
    RedisLockNoWait：所有使用该锁的，获取到锁才会执行，获取不到就不执行

    注意：默认锁住的最大时间是 60s，超过则释放

    使用示例：
        with RedisLock(lock_name=""):
            ...

        with RedisLockNoWait(lock_name=") as lock:
            if lock.lock_success:
                ...
"""
import redis
import uuid
import rediscluster
from typing import Union
from palp import settings


# redis 连接
class Redis:
    CONNECTION: Union[rediscluster.RedisCluster, redis.Redis] = None

    @classmethod
    def create_connection(cls):
        """
        创建 redis 连接

        :return:
        """
        if settings.REDIS_CLUSTER_NODES:
            pool = rediscluster.ClusterBlockingConnectionPool(
                startup_nodes=settings.REDIS_CLUSTER_NODES,
                password=settings.REDIS_PWD,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                **settings.REDIS_POOL_CONFIG
            )

            cls.CONNECTION = rediscluster.RedisCluster(connection_pool=pool, **settings.REDIS_CONFIG)
        else:
            pool = redis.BlockingConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PWD,
                db=settings.REDIS_DB,
                **settings.REDIS_POOL_CONFIG
            )

            cls.CONNECTION = redis.Redis(connection_pool=pool, decode_responses=True, **settings.REDIS_CONFIG)

    @classmethod
    def conn(cls) -> Union[rediscluster.RedisCluster, redis.Redis]:
        """
        用来获取连接

        :return:
        """
        if cls.CONNECTION is None:
            cls.create_connection()

        return cls.CONNECTION


# redis 等待锁
class RedisLock:
    def __init__(
            self,
            lock_name: str,
            block_timeout: int = None,
            wait_timeout: int = None,
            frequency: float = None
    ):
        """

        :param lock_name: 锁的名字
        :param block_timeout: 锁住的最大时间
        :param wait_timeout: 等待锁的最大时间
        :param frequency: 检查锁的频率
        """
        self._lock_name = lock_name
        self._block_timeout = block_timeout or 60
        self._wait_timeout = wait_timeout
        self._frequency = frequency or 0.1

        self._lock = Redis.conn().lock(
            name=self._lock_name,
            timeout=self._block_timeout,
            blocking_timeout=self._wait_timeout,
            sleep=self._frequency
        )

    def acquire(self):
        """
        获取锁

        :return:
        """
        return self._lock.acquire()

    def release(self):
        """
        释放锁

        :return:
        """
        return self._lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# redis 不等待锁
class RedisLockNoWait:
    def __init__(self, lock_name: str, block_timeout: int = None, auto_lock: bool = True):
        """

        :param lock_name: 锁的名字
        :param block_timeout: 锁住的最大时间
        :param auto_lock: 是否 with 时自动上锁
        """
        self._lock_name = lock_name
        self._block_timeout = block_timeout or 60
        self._auto_lock = auto_lock

        self.lock_success = False  # 是否成功上锁
        self._token = uuid.uuid1().hex.encode()

    def acquire(self) -> bool:
        """
        获取锁

        :return:
        """

        self.lock_success = bool(Redis.conn().set(
            name=self._lock_name,
            value=self._token,
            nx=True,
            ex=self._block_timeout
        ))

        return self.lock_success

    def release(self) -> bool:
        """
        释放锁

        :return:
        """
        if Redis.conn().get(self._lock_name) == self._token:
            return bool(Redis.conn().delete(self._lock_name))

        return False

    def exists(self) -> bool:
        """
        是否含有锁

        :return:
        """
        return bool(Redis.conn().exists(self._lock_name))

    def __enter__(self):
        self._auto_lock and self.acquire()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock_success and self.release()
