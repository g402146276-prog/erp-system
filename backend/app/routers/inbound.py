from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from app.database import get_db
from app.models.inbound import InboundRecord
from app.models.goods import Goods
from app.models.stock import Stock
from app.models.warehouse import Warehouse

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
    boniu_order_no: Optional[str] = None
    inbound_apply_id: Optional[int] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def update_stock(db: Session, warehouse_id: int, goods_id: int, quantity_change: int):
    stock = db.query(Stock).filter(
        Stock.warehouse_id == warehouse_id,
        Stock.goods_id == goods_id
    ).first()

    if stock:
        stock.quantity += quantity_change
    elif quantity_change > 0:
        stock = Stock(warehouse_id=warehouse_id, goods_id=goods_id, quantity=quantity_change)
        db.add(stock)
    # 如果 quantity_change <= 0 且无库存记录，直接忽略（不创建负值记录）


@router.get("/")
def list_inbounds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    warehouse_id: Optional[int] = None,
    goods_id: Optional[int] = None,
    bojun_order_no: Optional[str] = None,
    operator: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(
        InboundRecord,
        Goods.name.label("goods_name"),
        Goods.barcode.label("goods_barcode"),
        Warehouse.name.label("warehouse_name"),
    ).outerjoin(Goods, InboundRecord.goods_id == Goods.id
    ).outerjoin(Warehouse, InboundRecord.warehouse_id == Warehouse.id)

    if warehouse_id:
        query = query.filter(InboundRecord.warehouse_id == warehouse_id)
    if goods_id:
        query = query.filter(InboundRecord.goods_id == goods_id)
    if bojun_order_no:
        query = query.filter(InboundRecord.boniu_order_no.like(f"%{bojun_order_no}%"))
    if operator:
        query = query.filter(InboundRecord.operator.like(f"%{operator}%"))
    if date_from:
        query = query.filter(func.date(InboundRecord.created_at) >= date_from)
    if date_to:
        query = query.filter(func.date(InboundRecord.created_at) <= date_to)
    if keyword:
        query = query.filter(
            Goods.barcode.like(f"%{keyword}%") | Goods.name.like(f"%{keyword}%")
        )

    rows = query.order_by(InboundRecord.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for rec, goods_name, goods_barcode, warehouse_name in rows:
        result.append({
            "id": rec.id,
            "warehouse_id": rec.warehouse_id,
            "warehouse_name": warehouse_name or "",
            "goods_id": rec.goods_id,
            "goods_name": goods_name or "",
            "goods_barcode": goods_barcode or "",
            "quantity": rec.quantity,
            "boniu_order_no": rec.boniu_order_no or "",
            "operator": rec.operator or "",
            "remark": rec.remark or "",
            "created_at": rec.created_at,
        })
    return result


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
