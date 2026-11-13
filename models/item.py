from sqlalchemy import String, Float, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from database import Base


class ItemModel(Base):
    # SQLAlchemy ORM 模型(对应表 t_personal_todo)
    """个人待办事项表 ORM 模型，对应数据库表 t_personal_todo"""
    __tablename__ = "t_personal_todo"
    # 对象属性：类型 = 数据库字段
    # 待办事项的唯一标识符，用于后续的查询、更新和删除操作。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    creator: Mapped[str] = mapped_column(String(50), nullable=False, comment="创建者")
    # 用于补充说明任务的具体要求
    subject: Mapped[str] = mapped_column(String(225), nullable=False, comment="待办标题")
    # 用于补充说明任务的具体要求
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="待办详情")
    # 常见值包括 pending（待处理）、completed（已完成）、cancelled（已取消）。
    status: Mapped[str] = mapped_column(String(50), nullable=False, comment="任务状态")
    # 用于判断任务是否逾期
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="截止时间")
    # 用于触发通知推送。通常要求大于当前时间且早于截止时间。
    reminder_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="提醒时间")
    # high, medium, low 帮助用户区分任务轻重缓急
    priority: Mapped[str] = mapped_column(String(225), nullable=False, comment="优先级")
    # 用于多维度分类和筛选，如“工作”、“生活”、“紧急”
    tags: Mapped[str] = mapped_column(String(225), nullable=False, comment="标签列表")
