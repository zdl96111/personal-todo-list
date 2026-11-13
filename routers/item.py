from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_database
from crud import item as item_crud
from schemas.item import ItemCreate, ItemUpdate, ItemOut

# Item 相关 API 路由
# 注意：这里必须用 async def + AsyncSession，和 database.py 的异步会话保持一致

router = APIRouter(prefix="/items", tags=["待办事项管理"])

# 数据库会话（异步版本）
DbSession = Annotated[AsyncSession, Depends(get_database)]


@router.post("/", response_model=ItemOut, summary="新增待办事项")
async def create_item(item: ItemCreate, db: DbSession):
    return await item_crud.create_item(db, item)


@router.get("/", response_model=list[ItemOut], summary="待办事项列表（分页）")
async def list_items(
        db: DbSession,
        skip: int = Query(0, ge=0, title="跳过条数"),
        limit: int = Query(10, ge=1, le=100, title="返回条数"),
):
    return await item_crud.get_items(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemOut, summary="查询单个待办事项")
async def read_item(item_id: int, db: DbSession):
    db_item = await item_crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item项不存在")
    return db_item


@router.put("/{item_id}", response_model=ItemOut, summary="更新待办事项")
async def update_item(item_id: int, item: ItemUpdate, db: DbSession):
    db_item = await item_crud.update_item(db, item_id, item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item项不存在")
    return db_item


@router.delete("/{item_id}", summary="删除待办事项")
async def remove_item(item_id: int, db: DbSession):
    success = await item_crud.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item项不存在")
    return {"message": "删除成功", "item_id": item_id}
