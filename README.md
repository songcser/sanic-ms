# Sanic Micro Service

基于sanic的微服务基础架构

## Server

> 使用sanic异步框架，有比较高的性能，但是使用不当会造成blocking, 所以对于有IO请求的都要选用异步库。**添加库要慎重**

### Before Server Start

* 创建DB连接池
* 创建Client连接
* 创建queue, 用于日志追踪
* 创建opentracing.tracer进行日志追踪

### Middleware

* 处理跨域请求
* 创建span, 用于日志追踪
* 对response进行封装，统一格式

### Error Handler

对抛出的异常进行处理，返回统一格式

### Task

创建task消费queue中对span，用于日志追踪


### 异步框架
由于使用的是异步框架，可以将一些IO请求并行处理

### Example:

```
async def async_request(calls):
    results = await asyncio.gather(*[ call[2] for call in calls])
    for index, obj in enumerate(results):
        call = calls[index]
        call[0][call[1]] = results[index]


@visit_bp.get('/visit_tasks/<id:int>')
@doc.summary("获取拜访任务")
@doc.description("获取拜访任务")
@doc.produces({"result": VisitTaskApi})
async def get_visit_task(request, id):
    async with request.app.db.acquire(request) as cur:
        sql, params = select_sql('visit_task', id=id)
        data = await cur.fetchrow(sql, *params)
    calls = [
        [data, 'hospital_id', get_hospital_by_id(request, data['hospital_id'])],
        [data, 'city_id', get_city_by_id(request, data['city_id'])],
        [data, 'product_ids', get_products_by_ids(request, data['product_ids'])],
        [data, 'users_ids', get_users_by_id(request, data['users_ids'])],
        [data, 'literatures', get_literatures_by_ids(request, data['literatures'])],
        [data, 'questionnaires', get_questionnaires_by_ids(request, data['questionnaires'])],
        [data, 'feedbacks', get_feedbacks_by_ids(request, data['feedbacks'])],
    ]
    await async_request(calls)
    return data
```
get_hospital_by_id, get_city_by_id, get_products_by_ids等都是并行进行的。


#### 相关连接
[sanic](https://github.com/channelcat/sanic)


## DB 

> 使用asyncpg, 对数据库连接进行封装

### Example:

```
sql = "SELECT * FROM users WHERE name=$1"
name = "test"
async with request.app.db.acquire(request) as cur:
    data = await cur.fetchrow(sql, name)

async with request.app.db.transaction(request) as cur:
    data = await cur.fetchrow(sql, name)
```

* acquire() 函数为非事务, 对于只涉及到查询的使用非事务，可以提高查询效率
* tansaction() 函数为事务操作，对于增删改必须使用事务操作
* 传入request参数是为了获取到span，用于日志追踪
* TODO  数据库的读写分离

#### 相关连接
[asyncpg](https://github.com/MagicStack/asyncpg)

## Client

> 使用aiohttp中的client，对客户端进行了简单的封装

### Example: 

```
@app.listener('before_server_start')
async def before_srver_start(app, loop):
    app.client =  Client(loop, url=ODOO_MS)

cli = request.app.client.cli(request)
async with cli.get('/medicines?ids={}'.format(",".join([str(i) for i in ids]))) as res:
    return await res.json()

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.client.close()

```
Don’t create a session per request. Most likely you need a session per application which performs all requests altogether.

A session contains a connection pool inside, connection reusage and keep-alives (both are on by default) may speed up total performance.

对于访问不同的微服务可以创建多个不同的client，这样每个client都会keep-alives

#### 相关连接

[aiohttp](http://aiohttp.readthedocs.io/en/stable/client.html)


## Model & Migration

> ORM使用peewee, 但是只是用来做模型设计和migration, 数据操作使用asyncpg

### Example:

```
# migrations.py

from ethicall_common.migrations import MigrationModel, info, db

class BaseModel(Model):
    id = PrimaryKeyField()
    create_time = DateTimeField(verbose_name='创建时间', default=datetime.datetime.utcnow)

class BaseMigration(MigrationModel):
    _model = BaseModel

    @info(version="v1")
    def migrate_v1(self):
        migrate(self.add_column('name'))

def migrations():
    bm = BaseMigration()

    try:
        with db.transaction():
            bm.auto_migrate()
            print("Success Migration")
    except ProgrammingError as e:
        raise e
    except Exception as e:
        raise e

if __name__ == '__main__':
    migrations()
```

* 运行命令 python migrations.py
* migrate_v1函数添加字段name, 在BaseModel中要先添加name字段
* info装饰器会创建表migrate_record来记录migrate，version每个model中必须唯一，使用version来记录是否执行过，还可以记录author，datetime
* migrate函数必须以**migrate_**开头

#### 相关连接

[peewee](http://docs.peewee-orm.com/en/latest/)

## LOG

* 使用logging, 配置文件为logging.yml
* JsonFormatter将日志转成json格式，用于输入到ES

### 装饰器logger

```
@logger(type='method', category='test', detail='detail', description="des", tracing=True, level=logging.INFO)
async def get_hospital_by_id(request, id):
    cli = request.app.client.cli(request)
```

* type: 日志类型，如 method, route
* category: 日志类别，默认为app的name
* detail: 日志详细信息
* description: 日志描述，默认为函数的注释
* tracing: 日志追踪，默认为True
* level: 日志级别，默认为INFO

### 日志追踪

* 使用opentracing框架，但是在输出时转换成zipkin格式
* 日志追踪的span都是先放入queue中，在task中消费队列
* 对于DB，Client都加上了tracing

#### 相关连接

[opentracing](https://github.com/opentracing/opentracing-python)
[zipkin](https://github.com/openzipkin/zipkin)
[jaeger](https://uber.github.io/jaeger/)


## Test

> 单元测试使用unittest

### Example:

```
from ethicall_common.tests import APITestCase
from service.server import app

class TestCase(APITestCase):
    _app = app
    _blueprint = 'visit'

    def setUp(self):
        super(TestCase, self).setUp()
        self._mock.get('/hospitals/1',
                       payload={'id': 1, 'res_partner': {'name':'ddddd'}})

    def test_get_visit_task(self):
        data = self.get_visit_task_data('test3')
        res = self.client.create_visit_task(data=data)
        body = ujson.loads(res.text)
        self.assertEqual(body['status'], True)
        tid = body['data']['id']
        res = self.client.get_visit_task(id=tid)
        body = ujson.loads(res.text)
        self.assertEqual(body['status'], True)
        self.assertEqual(body['data']['name'], 'test3')

```

* 其中_blueprint为blueprint名称
* 在setUp函数中，使用_mock来注册mock信息, 这样就不会访问真实的服务器, payload为返回的body信息
* 使用client变量来访问各个函数, data为body信息，params为路径的参数信息，其他参数是route的参数

### coverage

```
coverage erase
coverage run --source service -m ethicall_common service.tests
coverage xml -o reports/coverage.xml
coverage2clover -i reports/coverage.xml -o reports/clover.xml
coverage html -d reports
```

* coverage2colver 是将coverage.xml 转换成 clover.xml，bamboo需要的格式是clover的。

#### 相关连接

[unittest](https://docs.python.org/3/library/unittest.html)
[coverage](https://coverage.readthedocs.io/en/coverage-4.4.1/)


## API

> api文档使用swagger

### Example:

```
from ethicall_common import doc

@visit_bp.get('/visit_tasks/<id:int>')
@doc.summary("获取拜访任务")
@doc.description("获取拜访任务")
@doc.produces({"data": VisitTaskApi})
async def get_visit_task(request, id):
    async with request.app.db.acquire(request) as cur:
        sql, params = select_sql('visit_task', id=id)
        data = await cur.fetchrow(sql, *params)
        return data

```

* summary: api概要
* description: 详细描述
* consumes: request的body数据
* produces: response的返回数据
* tag: API标签
* 在consumes和produces中传入的参数可以是peewee的model,会解析model生成API数据, 在field字段的help_text参数来表示引用对象
* http://localhost:8000/openapi/spec.json 获取生成的json数据

### Response

在返回时，不要返回response，直接返回原始数据，会在Middleware中对返回的数据进行处理，返回统一的格式，具体的格式可以[查看](http://wiki.ethicall.cn/pages/viewpage.action?pageId=8520132)

#### 相关连接

[swagger](https://swagger.io/)

## Exception

> 使用 app.error_handler = CustomHander() 对抛出的异常进行处理

### Example:

```
from ethicall_common.exception import ServerError

@visit_bp.delete('/visit_tasks/<id:int>')
async def del_visit_tqsk(request, id):
    raise ServerError(error='内部错误',code='10500', message="msg")
```

* code: 错误码，无异常时为0，其余值都为异常
* status_code: http状态码，使用标准的http状态码
* message: 状态码信息
* error: 自定义错误信息
