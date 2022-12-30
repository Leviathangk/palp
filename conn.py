"""
    项目连接创建处

    关于 redis
        这里的连接是懒加载的方式，使用的时候才会被引用，从而被创建（否则不同数据库的爬虫的连接将会是同一个库）
        redis_conn_lazy 是不指定连接 db 的 redis 使用方式：redis_conn_lazy.conn_to(0))

    关于 mongo
        mongo_conn.get_collection(db, col) 将会返回 Collection 对象（修改后的）

    关于 mysql、pg：
        mysql_conn 即 sqlalchemy 的 engine
        engine 有两个连接
            session：sqlalchemy 的连接
            connect：原始连接

        engin 是包装了一些方法的，部分如下：
            upsert
            update
            execute
            reverse_table_model：逆向表模型
"""
from palp import settings
from quickdb import RedisClusterConn
from quickdb import MongoConn, KafkaMsgProducer, RedisConnLazy
from quickdb import MysqlSQLAlchemyEngine, PostgreSQLAlchemyEngine

# redis 连接
redis_conn = None
redis_conn_lazy = None  # 不指定连接 db 的 redis

if settings.REDIS_HOST:
    if settings.REDIS_CLUSTER_NODES:
        redis_conn = RedisClusterConn(
            startup_nodes=settings.REDIS_CLUSTER_NODES,
            pwd=settings.REDIS_PWD,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            pool_kwargs=settings.REDIS_POOL_CONFIG,
            conn_kwargs=settings.REDIS_CONFIG
        ).conn
    else:
        # 更新一下最大连接数
        settings.REDIS_POOL_CONFIG.setdefault('max_connections', settings.REDIS_MAX_CONNECTIONS)

        redis_conn_lazy = RedisConnLazy(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            pwd=settings.REDIS_PWD,
            pool_kwargs=settings.REDIS_POOL_CONFIG,
            conn_kwargs=settings.REDIS_CONFIG
        )

        redis_conn = redis_conn_lazy.conn_to(settings.REDIS_DB)

# mysql 连接
mysql_conn = None

if settings.MYSQL_HOST:
    mysql_conn = MysqlSQLAlchemyEngine(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        db=settings.MYSQL_DB,
        user=settings.MYSQL_USER,
        pwd=settings.MYSQL_PWD,
        **settings.MYSQL_CONFIG
    )

# postgresql 连接
pg_conn = None

if settings.PG_HOST:
    pg_conn = PostgreSQLAlchemyEngine(
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        db=settings.PG_DB,
        user=settings.PG_USER,
        pwd=settings.PG_PWD,
        **settings.PG_CONFIG
    )

# mongo 连接
mongo_conn = None

if settings.MONGO_HOST:
    mongo_conn = MongoConn(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        user=settings.MONGO_USER,
        pwd=settings.MONGO_PWD,
        **settings.MONGO_CONFIG
    )

# kafka 连接
kafka_conn = None

if settings.KAFKA_SERVER:
    kafka_conn = KafkaMsgProducer(server=settings.KAFKA_SERVER, **settings.KAFKA_CONFIG)
