# Palp 文档
# 简介
Palp 是一个爬虫框架  
整体使用方式和 scrapy 类似，但有以下特点
- 同一个项目可以存放多个不同的 spider，spider 拥有各自的 settings
- 无感分布式，不需要内网，只需要 redis，分布式与非分布式仅继承的类不同
- 自动 cookiejar 仅需要使用 keep_session 即可
- 请求具备 3 中队列（先进先出、后进先出、优先级队列）

但有以下注意点：
- 默认不对 item、request 进行去重
- 去重为有严格去重（需开启），严格去重时，会有锁、分布式锁

# M、其它使用技巧  
## 1、增量爬虫
### 1.1 数据库判断
即通过自己保存的数据，进行判断列表页，已出现的 url 则为已抓取，那么后续则不需要抓取  
【案例】
```
is_repeat = False   # 重复标志

for i in response.xpath('//ul[@class="list_con"]//li'):
    notice_url = response.urljoin(i.xpath('./a/@href').extract_first())
    
    # 判断是否重复
    if conn_company_notice.find_one({'notice_url': notice_url}):
        is_repeat = True
        break
    
    yield palp.RequestGet(url=notice_url, callback=self.parse_content)

# 翻页
if not is_repeat and page_now < page_total:
    pass
```

### 1.2 redis 判断
Palp 默认的分布式去重有：
- redis set 去重
- redis bloom 去重（默认）

对应的过滤器如下：
- RequestRedisFilter：对应 redis set 去重
- RequestRedisBloomFilter：对应 redis bloom 去重

使用时需开启以下设置，作用是开启去重并持久化
```
REQUEST_FILTER = True
PERSISTENCE_REQUEST_FILTER = True
```
【案例】以 redis bloom 去重 为例  
注意：虽然本身会做去重请求，但是之所以这样写，是为了避免再去翻页浪费时间
```
from palp.filter import RequestRedisBloomFilter

is_repeat = False   # 重复标志

for i in response.xpath('//ul[@class="list_con"]//li'):
    notice_url = response.urljoin(i.xpath('./a/@href').extract_first())
    
    req = palp.RequestGet(url=notice_url, callback=self.parse_content)

    # 判断是否重复
    if RequestRedisBloomFilter().is_repeat(req):
        break
    
    yield req

# 翻页
if not is_repeat and page_now < page_total:
    pass
```

## 2、指定域名添加代理
request 有一个 add_proxy 方法，该方法有两个参数
- proxies：代理，不给则使用默认
- allow_domains：允许的域名列表  

注意：使用了 allow_domains 则不在 allow_domains 内的将不会被加代理

【案例】
```
class RequestMiddleware(palp.RequestMiddleware):
    def request_in(self, spider, request) -> None:
        """
        请求进入时的操作

        :param spider:
        :param request:
        :return:
        """
        allow_domains = ['xxx']
        request.add_proxy(allow_domains=allow_domains)
```

## 3、快速二次请求
基于上一次请求的基础上进行二次请求  
有两种方法：
- 原地修改
- request 的 to_dict() 方法获取字典后修改

### 3.1、原地修改
```
def parse(self, request, response) -> None:
    request.xxx = xxx   # 修改

    yield request
```

### 3.2、to_dict()
```
request_dict = request.to_dict()
request_dict[xxx] = xxx # 修改

yield palp.Request(**request_dict)
```