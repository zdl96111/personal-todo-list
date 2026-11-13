from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers.item import router as item_router
from database import create_tables, async_engine


# 6. 使用 lifespan 管理应用生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动阶段
    print("应用启动中...")
    await create_tables()
    yield
    # 关闭阶段
    print("应用关闭，释放数据库连接...")
    await async_engine.dispose()


# 7. 初始化 FastAPI 应用
app = FastAPI(title="=====个人待办API=====", lifespan=lifespan)
# 注册路由
app.include_router(item_router)


# 根路径，提示欢迎信息
@app.get("/", tags=["首页"], summary="欢迎信息")
async def read_root():
    return {"message": "欢迎使用个人待办 API", "docs": "/docs"}


