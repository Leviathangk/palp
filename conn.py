"""
    项目连接创建处

    sqlalchemy 有两个连接
        session：sqlalchemy 的连接
        connect：原始连接

    methods 是包装了一些方法的，部分如下：
        upsert
        update
        execute
        reverse_table_model：逆向表模型
"""
from palp import settings
from quickdb import RedisConn, RedisClusterConn
from quickdb import MysqlSQLAlchemyEngine, MysqlSQLAlchemyMethods
from quickdb import PostgreSQLAlchemyEngine, PostgreSQLAlchemyMethods

# redis 连接
if settings.REDIS_CLUSTER_NODES:
    redis_conn = RedisClusterConn(
        startup_nodes=settings.REDIS_CLUSTER_NODES,
        pwd=settings.REDIS_PWD,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        pool_kwargs=settings.REDIS_POOL_CONFIG,
        conn_kwargs=settings.REDIS_CONFIG
    )
else:
    redis_conn = RedisConn(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        pwd=settings.REDIS_PWD,
        db=settings.REDIS_DB,
        pool_kwargs=settings.REDIS_POOL_CONFIG,
        conn_kwargs=settings.REDIS_CONFIG
    )

# mysql 连接
if settings.MYSQL_HOST:
    mysql_conn = MysqlSQLAlchemyEngine(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_HOST,
        db=settings.MYSQL_HOST,
        user=settings.MYSQL_HOST,
        pwd=settings.MYSQL_HOST,
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
        port=settings.PG_HOST,
        db=settings.PG_HOST,
        user=settings.PG_HOST,
        pwd=settings.PG_HOST,
        **settings.PG_CONFIG
    )
    mysql_method = PostgreSQLAlchemyMethods(engine=pg_conn)
else:
    pg_conn = None
    mysql_method = None
