from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.inbound import InboundRecord
from app.models.stock import Stock

router = APIRouter(prefix="/api/inbound", tags=["入库管理"])


class InboundCreate(BaseModel):
    warehouse_id: int
    goods_id: int
    quantity: int
    boniu_order_no: str = None
    inbound_apply_id: int = None
    operator: str = None
    remark: str = None


class InboundResponse(BaseModel):
    id: int
    warehouse_id: int
    goods_id: int
    quantity: int
    boniu_order_no: str = None
    inbound_apply_id: int = None
    operator: str = None
    remark: str = None
    created_at: datetime = None

    class Config:
        from_attributes = True


def update_stock(db: Session, warehouse_id: int, goods_id: int, quantity_change: int):
    stock = db.query(Stock).filter(
        Stock.warehouse_id == warehouse_id,
        Stock.goods_id == goods_id
    ).first()

    if stock:
        stock.quantity += quantity_change
    else:
        stock = Stock(warehouse_id=warehouse_id, goods_id=goods_id, quantity=quantity_change)
        db.add(stock)

    db.commit()


@router.get("/", response_model=List[InboundResponse])
def list_inbounds(skip: int = 0, limit: int = 100, warehouse_id: int = None, goods_id: int = None, db: Session = Depends(get_db)):
    query = db.query(InboundRecord)
    if warehouse_id:
        query = query.filter(InboundRecord.warehouse_id == warehouse_id)
    if goods_id:
        query = query.filter(InboundRecord.goods_id == goods_id)
    inbounds = query.order_by(InboundRecord.created_at.desc()).offset(skip).limit(limit).all()
    return inbounds


@router.get("/{inbound_id}", response_model=InboundResponse)
def get_inbound(inbound_id: int, db: Session = Depends(get_db)):
    inbound = db.query(InboundRecord).filter(InboundRecord.id == inbound_id).first()
    if not inbound:
        raise HTTPException(status_code=404, detail="入库记录不存在")
    return inbound


@router.post("/", response_model=InboundResponse)
def create_inbound(inbound_data: InboundCreate, db: Session = Depends(get_db)):
    inbound = InboundRecord(**inbound_data.model_dump())
    db.add(inbound)
    db.commit()
    db.refresh(inbound)

    update_stock(db, inbound.warehouse_id, inbound.goods_id, inbound.quantity)

    return inbound


@router.delete("/{inbound_id}")
def delete_inbound(inbound_id: int, db: Session = Depends(get_db)):
    inbound = db.query(InboundRecord).filter(InboundRecord.id == inbound_id).first()
    if not inbound:
        raise HTTPException(status_code=404, detail="入库记录不存在")

    update_stock(db, inbound.warehouse_id, inbound.goods_id, -inbound.quantity)

    db.delete(inbound)
    db.commit()
    return {"message": "删除成功"}
