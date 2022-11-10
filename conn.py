"""
    项目连接创建处

    关于 redis
        这里的连接是懒加载的方式，使用的时候才会被引用，从而被创建（否则不同数据库的爬虫的连接将会是同一个库）

    关于 mongo
        mongo_conn.get_collection(db, col) 将会返回 Collection 对象（修改后的）

    关于 mysql、pg：
        mysql_conn 即 sqlalchemy 的 engine
        engine 有两个连接
            session：sqlalchemy 的连接
            connect：原始连接

        mysql_method 是包装了一些方法的，部分如下：
            upsert
            update
            execute
            reverse_table_model：逆向表模型
"""
from palp import settings
from quickdb import MongoConn, KafkaMsgProducer
from quickdb import RedisConn, RedisClusterConn
from quickdb import MysqlSQLAlchemyEngine, MysqlSQLAlchemyMethods
from quickdb import PostgreSQLAlchemyEngine, PostgreSQLAlchemyMethods

# redis 连接
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
        redis_conn = RedisConn(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            pwd=settings.REDIS_PWD,
            db=settings.REDIS_DB,
            pool_kwargs=settings.REDIS_POOL_CONFIG,
            conn_kwargs=settings.REDIS_CONFIG
        ).conn
else:
    redis_conn = None

# mysql 连接
if settings.MYSQL_HOST:
    mysql_conn = MysqlSQLAlchemyEngine(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        db=settings.MYSQL_DB,
        user=settings.MYSQL_USER,
        pwd=settings.MYSQL_PWD,
        **settings.MYSQL_CONFIG
    )
    mysql_method = MysqlSQLAlchemyMethods(engine=mysql_conn)
else:
    mysql_conn = None
    mysql_method = None

# postgresql 连接
if settings.PG_HOST:
    pg_conn = PostgreSQLAlchemyEngine(
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        db=settings.PG_DB,
        user=settings.PG_USER,
        pwd=settings.PG_PWD,
        **settings.PG_CONFIG
    )
    pg_method = PostgreSQLAlchemyMethods(engine=pg_conn)
else:
    pg_conn = None
    pg_method = None

# mongo 连接
if settings.MONGO_HOST:
    mongo_conn = MongoConn(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        user=settings.MONGO_USER,
        pwd=settings.MONGO_PWD,
        **settings.MONGO_CONFIG)
else:
    mongo_conn = None

# kafka 连接
if settings.KAFKA_SERVER:
    kafka_conn = KafkaMsgProducer(server=settings.KAFKA_SERVER, **settings.KAFKA_CONFIG)
else:
    kafka_conn = None
