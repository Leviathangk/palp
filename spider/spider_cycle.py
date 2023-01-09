"""
    周期性爬虫

    更新设置，添加中间件
    # 启用则修改 task 表中对应任务的失败、生成状态
    REQUEST_MIDDLEWARE = {
        1: "palp.middleware.CycleSpiderRecordMiddleware",
    }

    # 启用则生成、汇总 record 表单批次爬取记录
    SPIDER_MIDDLEWARE = {
        1: 'palp.middleware.CycleSpiderRecordMiddleware',
    }

    示例
        class DemoSpider(CycleSpider, palp.LocalSpider):
            spider_name = "baidu3"  # 自定义的名字
            spider_domains = []  # 允许通过的域名，默认不限制
            spider_settings = None  # 字典形式或导入形式的设置
            spider_table_task_name = f'palp_cycle_task_{spider_name}'  # 任务表
            spider_table_record_name = f'palp_cycle_record_{spider_name}'  # 记录表

            def start_requests(self) -> None:
                self.initialize_all_task_states()   # 重置所有任务状态为 0

                # 获取任务状态为 0 的任务
                for task in self.get_tasks_state0():
                    print(task)
                    yield palp.RequestGet(url=task['task'])

            def parse(self, request, response) -> None:
                print(response)


        if __name__ == '__main__':
            DemoSpider.create_mysql_table()    # 快捷创建表
            DemoSpider.insert_tasks(['https://www.baidu.com', 'https://www.jd.com'])   # 快捷插入任务
            DemoSpider(thread_count=1).start()
"""
from palp import settings
from typing import Union, List


class CycleSpider:
    """
        周期性爬虫，需被继承，同时继承其余爬虫
    """
    spider_table_task_name = None  # 任务表
    spider_table_record_name = None  # 记录表
    spider_table_record_max_id = None  # 记录表 id

    @classmethod
    def initialize_all_task_states(cls):
        """
            重置所有的任务状态为 0
        """
        from palp.conn import mysql_conn

        sql = f'''
            UPDATE `{cls.spider_table_task_name}` 
            SET state = 0
            WHERE state != 0;
        '''

        mysql_conn.execute(sql)

    @classmethod
    def get_tasks(cls, state: int, count: int = 1000) -> dict:
        """
        寻找任务

        :param state: 数据库内的状态
        :param count: 限制单次获取大小
        :return: 数据库字典
        """
        from palp.conn import mysql_conn

        sql = f'''
            SELECT
                * 
            FROM
                `{cls.spider_table_task_name}`
            WHERE
                state = {state}
            LIMIT {count} ;
        '''

        tasks = mysql_conn.execute(sql=sql, fetchall=True, back_dict=True)
        if tasks:
            for task in tasks:
                cls.set_task_state_running(task_id=task['id'])
                yield task

    @classmethod
    def get_tasks_state0(cls, count: int = 1000) -> dict:
        """
        寻找未做的任务（state 为 0 的）

        :param count: 限制单次获取大小
        :return: 数据库字典
        """
        for task in cls.get_tasks(state=0, count=count):
            yield task

    @classmethod
    def get_tasks_state2(cls, count: int = 1000) -> dict:
        """
        获取之前失败的任务（state 为 2 的）

        :param count: 限制单次获取大小
        :return: 数据库字典
        """
        for task in cls.get_tasks(state=2, count=count):
            yield task

    @classmethod
    def set_task_state(cls, task_id: int, state: int) -> None:
        """
        设置任务状态

        :param task_id: task 表的 id
        :param state: task 表的 state
        :return:
        """
        from palp.conn import mysql_conn

        sql = f'''
        UPDATE `{cls.spider_table_task_name}` 
        SET state = {state} 
        WHERE
            id = {task_id};
        '''

        mysql_conn.execute(sql)

    @classmethod
    def set_task_state_running(cls, task_id: int) -> None:
        """
        设置任务状态为 1 抓取中

        :param task_id: task 表的 id
        :return:
        """
        cls.set_task_state(task_id=task_id, state=1)

    @classmethod
    def set_task_state_done(cls, task_id: int) -> None:
        """
        设置任务状态为 2 抓取完毕

        :param task_id: task 表的 id
        :return:
        """
        cls.set_task_state(task_id=task_id, state=2)

    @classmethod
    def set_task_state_failed(cls, task_id: int) -> None:
        """
        设置任务状态为 3 抓取失败

        :param task_id: task 表的 id
        :return:
        """
        cls.set_task_state(task_id=task_id, state=3)

    @classmethod
    def create_mysql_table(cls):
        """
            创建周期爬取表
        """
        from palp.conn import mysql_conn

        # 创建 mysql task 表
        if not cls.check_mysql_table_exists(table_name=cls.spider_table_task_name):
            sql = f'''
                CREATE TABLE `{cls.spider_table_task_name}` (
                  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
                  `task` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '任务',
                  `state` int DEFAULT '0' COMMENT '0 待抓取，1抓取中，2抓取完毕，3抓取失败',
                  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `task_unique` (`task`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Palp {cls.spider_name} 周期爬取表';
            '''
            mysql_conn.execute(sql=sql)

        # 创建 mysql 记录表
        if not cls.check_mysql_table_exists(table_name=cls.spider_table_record_name):
            sql = f'''
                CREATE TABLE `{cls.spider_table_record_name}` (
                  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
                  `total` int DEFAULT NULL COMMENT '任务总数',
                  `succeed` int DEFAULT NULL COMMENT '任务成功总数',
                  `failed` int DEFAULT NULL COMMENT '任务失败总数',
                  `is_done` int DEFAULT '0' COMMENT '0执行中，1执行完毕',
                  `start_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '执行开始时间',
                  `end_time` datetime DEFAULT NULL COMMENT '执行结束时间',
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Palp {cls.spider_name} 周期记录表';
            '''
            mysql_conn.execute(sql=sql)

    @classmethod
    def check_mysql_table_exists(cls, table_name: str) -> bool:
        """
        检查 mysql 是否存在指定表

        :param table_name: 表名
        :return:
        """
        from palp.conn import mysql_conn

        sql = f'''
            SELECT
                table_name 
            FROM
                information_schema.TABLES 
            WHERE
                table_name = '{table_name}';
        '''
        res = mysql_conn.execute(sql=sql, fetchone=True)
        if res:
            return True

        return False

    @classmethod
    def insert_tasks(cls, tasks: Union[List[str], str]):
        """
        插入任务
        注意：任务不能重复，因为 task 是唯一键（插入使用了 IGNORE 所以不会报错）

        :param tasks: 存放在 task 字段的任务
        :return:
        """
        from palp.conn import mysql_conn

        if isinstance(tasks, str):
            tasks = [tasks]

        # 组合 sql
        sql = f'''
            INSERT IGNORE INTO `{cls.spider_table_task_name}` ( task )
            VALUES
        '''
        for task in tasks:
            sql += f"\n( '{task}' ),"

        sql = sql.rstrip(',') + ';'
        mysql_conn.execute(sql=sql)

    @classmethod
    def insert_task_record_start(cls):
        """
        插入初始记录

        :return:
        """
        from palp.conn import mysql_conn

        sql = f'''
            INSERT INTO `{cls.spider_table_record_name}` ( is_done,start_time )
            VALUES(0,now());
        '''
        mysql_conn.execute(sql=sql)

    @classmethod
    def update_task_record(cls, total: int, succeed: int, failed: int):
        """
        更新记录表

        :param total: 总量
        :param succeed: 成功量
        :param failed: 失败量
        :return:
        """
        from palp.conn import mysql_conn

        max_id = cls.get_spider_table_record_max_id()

        sql = f'''
            UPDATE `{cls.spider_table_record_name}` 
            SET total = {total},
            succeed = {succeed}, 
            failed = {failed} 
            WHERE
                id = {max_id};
        '''
        mysql_conn.execute(sql=sql)

    @classmethod
    def update_task_record_end(cls):
        """
        设置记录结束

        :return:
        """
        from palp.conn import mysql_conn

        max_id = cls.get_spider_table_record_max_id()

        sql = f'''
            UPDATE `{cls.spider_table_record_name}` 
            SET is_done = 1,
            end_time = now() 
            WHERE
                id = {max_id};
        '''
        mysql_conn.execute(sql=sql)

    @classmethod
    def delete_task(cls, task_id: int):
        """
        删除任务

        :param task_id: 任务 id
        :return:
        """
        from palp.conn import mysql_conn

        # 组合 sql
        sql = f'''
            DELETE
            FROM
              `{cls.spider_table_task_name}`
            WHERE
              id = {task_id};
        '''
        mysql_conn.execute(sql=sql)

    @classmethod
    def get_spider_table_record_max_id(cls):
        """
        记录表最大 id

        :return:
        """
        from palp.conn import mysql_conn

        if cls.spider_table_record_max_id is None:
            sql = f'''
                SELECT
                    max( id ) 
                FROM
                    `{cls.spider_table_record_name}`
            '''

            res = mysql_conn.execute(sql=sql, fetchone=True)

            if res:
                cls.spider_table_record_max_id = res[0]

        return cls.spider_table_record_max_id
