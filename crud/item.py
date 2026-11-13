from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.item import ItemModel
from schemas.item import ItemCreate, ItemUpdate


# 数据库 CRUD 操作（全部为异步，配合 AsyncSession 使用）
# 关键：AsyncSession 的 commit / refresh / delete / execute 都是协程，必须 await

# -------- 增（Create）--------
async def create_item(db: AsyncSession, item: ItemCreate) -> ItemModel:
    # 请求体转成 ORM 对象；id 由数据库自增，不要从前端传
    db_item = ItemModel(**item.model_dump())
    db.add(db_item)          # add 是同步方法，不需要 await
    await db.commit()        # 提交事务（真正写库）
    await db.refresh(db_item)  # 从数据库读回自增 id、create_time 等
    return db_item


# -------- 查（Read）--------
async def get_item(db: AsyncSession, item_id: int) -> ItemModel | None:
    result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
    return result.scalar_one_or_none()


async def get_items(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[ItemModel]:
    result = await db.execute(select(ItemModel).offset(skip).limit(limit))
    return list(result.scalars().all())


# -------- 改（Update）--------
async def update_item(db: AsyncSession, item_id: int, item: ItemUpdate) -> ItemModel | None:
    db_item = await get_item(db, item_id)
    if not db_item:
        return None
    # 只更新客户端实际传了的字段
    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    await db.commit()
    await db.refresh(db_item)
    return db_item


# -------- 删（Delete）--------
async def delete_item(db: AsyncSession, item_id: int) -> bool:
    db_item = await get_item(db, item_id)
    if not db_item:
        return False
    await db.delete(db_item)
    await db.commit()
    return True
