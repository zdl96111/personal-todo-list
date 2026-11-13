"""
pytest 公共配置

这个文件里的东西，pytest 会自动加载，不需要在任何地方 import。

三个 fixture（被 @pytest.fixture 标记的函数）：
    engine   → 测试用的内存数据库引擎
    session  → 每个测试用的事务会话
    client   → 可以发 HTTP 请求的异步客户端

关键点：测试**不连 MySQL**，用 SQLite 内存库，跑完就没了，不留脏数据。
"""

import sys
from pathlib import Path

# 让 pytest 能找到项目根目录下的 database / models / routers 等模块
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from database import Base, get_database
from main import app

# 引入模型，让 Base.metadata 知道有哪些表要建
from models.item import ItemModel  # noqa: F401


@pytest_asyncio.fixture
async def engine():
    """每个测试函数用一个全新的内存数据库。

    sqlite+aiosqlite:// 后面不写路径 = 纯内存库。
    StaticPool 让所有连接复用同一个内存库（否则每个连接都是独立的空库）。
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """测试用的数据库会话。"""
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session):
    """替换掉真实的数据库依赖，返回一个可以发请求的客户端。

    app.dependency_overrides 是 FastAPI 提供的「依赖替换」机制：
    原本 get_database 会连 MySQL，这里替换成用测试 session。
    """

    async def override_get_database():
        yield session

    app.dependency_overrides[get_database] = override_get_database

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
