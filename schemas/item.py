from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Pydantic 模型（请求/响应校验）

class ItemCreate(BaseModel):
    """新增个人待办事项时的请求体

    注意：不要带 id —— 主键由数据库自增；带了反而容易冲突。
    """
    creator: str = Field(..., min_length=2, max_length=50, description="创建者，2~50个字符")
    subject: str = Field(..., min_length=2, max_length=50, description="待办标题，2~50个字符")
    description: str | None = Field(None, max_length=225, description="待办详情，最长225个字符，可不填")
    status: str = Field("pending", max_length=50, description="任务状态，如 pending/completed/cancelled")
    deadline: datetime | None = Field(None, description="截止时间，可不填")
    reminder_time: datetime | None = Field(None, description="提醒时间，可不填")
    priority: str = Field("medium", max_length=200, description="优先级 high/medium/low")
    tags: str = Field("", max_length=200, description="标签列表，逗号分隔")


class ItemUpdate(BaseModel):
    """更新个人待办事项时的请求体（字段均可选，只传要改的）"""
    subject: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = Field(None, max_length=225)
    status: str | None = Field(None, max_length=50)
    deadline: datetime | None = None
    reminder_time: datetime | None = None
    priority: str | None = Field(None, max_length=200)
    tags: str | None = Field(None, max_length=200)


class ItemOut(BaseModel):
    """返回给客户端的数据结构"""
    id: int
    creator: str
    subject: str
    description: str | None = None
    status: str
    deadline: datetime | None = None
    reminder_time: datetime | None = None
    priority: str
    tags: str
    create_time: datetime | None = None
    update_time: datetime | None = None

    # from_attributes=True 允许 Pydantic 直接从 SQLAlchemy ORM 对象读取属性
    model_config = ConfigDict(from_attributes=True)
