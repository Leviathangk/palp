# palp
一个爬虫框架\
它与 scrapy 使用方式大部分是一致的\
它是在了解大概的架构之后全新设计的，与 scrapy 等框架，使用相似降低了学习成本

主要有以下差异：\
1.它具备更多的语法提示\
2.它的普通爬虫和分布式爬虫，只需要切换继承，而没有其它任何操作，0 成本分布式\
3.同一个项目兼容不同的爬虫，每个爬虫都拥有独立的设置而互不影响

未来将适配更多快捷方法，暂时个人使用，欢迎大家试用并给出实用性的意见

# 安装
pip install palp

# 创建项目
palp create -p xxx

# 创建 spider
palp create -s xxx
