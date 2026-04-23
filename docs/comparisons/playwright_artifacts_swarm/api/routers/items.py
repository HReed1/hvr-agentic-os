from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from api.database import get_db
from api import models, schemas

router = APIRouter(
    prefix="/items",
    tags=["items"],
)

@router.post("/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = models.Item(name=item.name)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[schemas.Item])
async def read_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Item))
    return result.scalars().all()
