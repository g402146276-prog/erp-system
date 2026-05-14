from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.goods import Goods

router = APIRouter(prefix="/api/goods", tags=["商品管理"])


class GoodsCreate(BaseModel):
    barcode: str
    name: str
    spec: str = None
    unit: str = "个"
    category: str = None
    price: float = 0
    remark: str = None


class GoodsUpdate(BaseModel):
    name: str = None
    spec: str = None
    unit: str = None
    category: str = None
    price: float = None
    remark: str = None


class GoodsResponse(BaseModel):
    id: int
    barcode: str
    name: str
    spec: str = None
    unit: str
    category: str = None
    price: float
    remark: str = None
    created_at: datetime = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[GoodsResponse])
def list_goods(skip: int = 0, limit: int = 200, keyword: str = None, db: Session = Depends(get_db)):
    query = db.query(Goods)
    if keyword:
        query = query.filter(
            or_(Goods.name.contains(keyword), Goods.barcode.contains(keyword))
        )
    goods = query.offset(skip).limit(limit).all()
    return goods


@router.get("/{goods_id}", response_model=GoodsResponse)
def get_goods(goods_id: int, db: Session = Depends(get_db)):
    goods = db.query(Goods).filter(Goods.id == goods_id).first()
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")
    return goods


@router.get("/barcode/{barcode}", response_model=GoodsResponse)
def get_goods_by_barcode(barcode: str, db: Session = Depends(get_db)):
    goods = db.query(Goods).filter(Goods.barcode == barcode).first()
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")
    return goods


@router.post("/", response_model=GoodsResponse)
def create_goods(goods_data: GoodsCreate, db: Session = Depends(get_db)):
    existing = db.query(Goods).filter(Goods.barcode == goods_data.barcode).first()
    if existing:
        raise HTTPException(status_code=400, detail="条码已存在")

    goods = Goods(**goods_data.model_dump())
    db.add(goods)
    db.commit()
    db.refresh(goods)
    return goods


@router.put("/{goods_id}", response_model=GoodsResponse)
def update_goods(goods_id: int, goods_data: GoodsUpdate, db: Session = Depends(get_db)):
    goods = db.query(Goods).filter(Goods.id == goods_id).first()
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")

    update_data = goods_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goods, key, value)

    db.commit()
    db.refresh(goods)
    return goods


@router.delete("/{goods_id}")
def delete_goods(goods_id: int, db: Session = Depends(get_db)):
    goods = db.query(Goods).filter(Goods.id == goods_id).first()
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")

    db.delete(goods)
    db.commit()
    return {"message": "删除成功"}
