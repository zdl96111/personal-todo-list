from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func


# 数据库连接与 Session 管理
# 1.定义数据库连接URL 用户名和密码填自己的
ASYNC_DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/db_fastapi_pro?charset=utf8"

# 2.使用 create_async_engine 创建异步引擎
async_engine = create_async_engine(
	ASYNC_DATABASE_URL,
	echo=True,          # 可选，开发环境开启输出 SQL 日志
	pool_size=10,       # 设置连接池活跃的连接数
	max_overflow=20,     # 设置连接池允许创建的额外连接数
	pool_pre_ping=True  # 防止连接过期
)

# 3.创建异步会话工厂
async_session_local = async_sessionmaker(  # 工厂函数
	bind=async_engine,  # 绑定数据库引擎
	class_=AsyncSession,  # 指定会话类
	expire_on_commit=False  # 提交后会话对象不过期，不会重新查询数据库
)

# 4.定义模型类
# 4.1基类：创建时间，更新时间； 继承 DeclarativeBase（包含通用属性和字段的映射）
class Base(DeclarativeBase):
	create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="创建时间")
	update_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="修改时间")

# 5. 定义建表函数 → FastAPI启动的时候调用建表的函数
async def create_tables():
	"""
	在应用启动时自动创建所有继承自 Base 的表，已创建的不会再创建
	"""
	# 获取数据库的异步引擎，开启事务，执行ORM操作，建表
	async with async_engine.begin() as conn:	# 第一步创建的异步引擎
		# 在应用启动时执行 Base.metadata.create_all() ，SQLAlchemy 会根据模型自动创建表：
		await conn.run_sync(Base.metadata.create_all)  # Base模型类的元数据创建
	print(" 数据库表创建/检查完成")

# 1.创建依赖项
async def get_database():
	async with async_session_local() as session:
		try:
			yield session  # 返回数据库会话(session)给路由处理函数
		except Exception as e:
			await session.rollback()  # 有异常，会话回滚
			raise e
		finally:
			await session.close()  # 会话关闭
