# 个人待办 API

一个用 FastAPI + SQLAlchemy（异步）+ MySQL 写的个人待办事项后端。

## 技术栈

| 层 | 选型 |
|---|---|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.x（异步，`AsyncSession`） |
| 数据库 | MySQL 8 + `aiomysql` 驱动 |
| 校验 | Pydantic v2 |
| 运行 | uvicorn |

## 项目结构

```
.
├── main.py              # 应用入口、lifespan、根路由
├── database.py          # 异步引擎、会话工厂、Base、建表、依赖注入
├── models/
│   └── item.py          # ORM 模型：ItemModel → 表 t_personal_todo
├── schemas/
│   └── item.py          # Pydantic 模型：ItemCreate / ItemUpdate / ItemOut
├── crud/
│   └── item.py          # 数据库操作（全异步）
├── routers/
│   └── item.py          # 路由：/items 下的一组接口
├── requirements.txt
└── .gitignore
```

分层职责：**路由只做参数接收与异常转换，CRUD 只做数据库操作，Schema 只做校验与序列化。**

## 快速开始

### 1. 准备数据库

```sql
CREATE DATABASE db_fastapi_pro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 修改连接串

`database.py` 第 12 行：

```python
ASYNC_DATABASE_URL = "mysql+aiomysql://用户名:密码@localhost:3306/db_fastapi_pro?charset=utf8"
```

> 生产环境建议改成从环境变量读取：`os.getenv("DATABASE_URL")`。

### 3. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 4. 启动

```bash
uvicorn main:app --reload --port 8000
```

启动时会自动建表（`Base.metadata.create_all`，已存在的表不会重复创建）。

打开 <http://127.0.0.1:8000/docs> 即可在浏览器里测试所有接口。

## 接口列表

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 欢迎信息 |
| POST | `/items/` | 新增待办 |
| GET | `/items/` | 列表（支持 `skip` / `limit` 分页） |
| GET | `/items/{item_id}` | 查询单条 |
| PUT | `/items/{item_id}` | 部分更新（只传要改的字段） |
| DELETE | `/items/{item_id}` | 删除 |

## 请求示例

新增（`id`、`create_time`、`update_time` 由数据库/ORM 自动生成，不用传）：

```json
{
  "creator": "大肥鱼",
  "subject": "写代码",
  "description": "把 CRUD 改成异步",
  "status": "pending",
  "deadline": "2026-11-20T18:00:00",
  "reminder_time": "2026-11-20T17:00:00",
  "priority": "high",
  "tags": "学习"
}
```

只有 `creator` 和 `subject` 是必填，其余都有默认值或可为 `null`。

响应：

```json
{
  "id": 1,
  "creator": "大肥鱼",
  "subject": "写代码",
  "status": "pending",
  "create_time": "2026-11-13T22:23:02",
  "update_time": "2026-11-13T22:23:02"
}
```

## 设计说明

### 为什么全部用异步

`database.py` 用的是 `create_async_engine` + `AsyncSession`。异步会话的 `commit()`、`refresh()`、`execute()`、`delete()` 都是**协程**，必须 `await`；漏掉 `await` 不会报语法错误，但操作不会真正执行（表现为返回字段全是 `null`）。

因此：

- `crud/*` 里所有函数都是 `async def`
- `routers/*` 里所有接口也是 `async def`
- 依赖注入声明的类型是 `AsyncSession`（不是 `Session`）
- 查询用 `select()`，不用 `session.query()`

### 时间字段

`models/item.py` 继承的 `Base` 里定义了：

```python
create_time = mapped_column(DateTime, default=func.now(), comment="创建时间")
update_time = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="修改时间")
```

`onupdate` 会在每次 UPDATE 时自动刷新 `update_time`，不需要业务代码手动赋值。

注意：`default` 和 `insert_default` 不能同时写，否则 SQLAlchemy 2.1 会抛 `ArgumentError`。

### 错误处理

- 参数不合法 → FastAPI 自动返回 `422`（由 Pydantic 校验）
- 资源不存在 → 路由里 `raise HTTPException(404, "Item项不存在")`
- 数据库异常 → 依赖 `get_database` 里 `rollback` 后重新抛出

## 后续可以做的事

- [ ] 把数据库连接串移到 `.env`
- [ ] 加 `pytest` 测试（用 SQLite 内存库跑 CRUD）
- [ ] 加用户认证（JWT）
- [ ] `status` 字段用枚举约束（`Literal["pending", "completed", "cancelled"]`）
- [ ] 加 Docker Compose，一条命令起「应用 + MySQL」
