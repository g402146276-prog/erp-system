from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.purchase_inbound import PurchaseInbound
from app.models.goods import Goods
from app.models.stock import Stock
from app.models.inbound import InboundRecord
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/purchase-inbound", tags=["采购入库"])


class PurchaseCreate(BaseModel):
    bojun_order_no: str
    goods_id: int
    received_quantity: int
    warehouse_id: int
    remark: Optional[str] = None


@router.post("/")
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """记录一次采购入库，同时增加库存"""
    record = PurchaseInbound(
        bojun_order_no=data.bojun_order_no,
        goods_id=data.goods_id,
        received_quantity=data.received_quantity,
        operator=current_user.display_name,
        remark=data.remark,
    )
    db.add(record)

    # 同步增加库存
    stock = db.query(Stock).filter(
        Stock.warehouse_id == data.warehouse_id,
        Stock.goods_id == data.goods_id,
    ).first()
    if stock:
        stock.quantity += data.received_quantity
    else:
        stock = Stock(
            warehouse_id=data.warehouse_id,
            goods_id=data.goods_id,
            quantity=data.received_quantity,
        )
        db.add(stock)

    # 写入入库记录
    inbound_rec = InboundRecord(
        warehouse_id=data.warehouse_id,
        goods_id=data.goods_id,
        quantity=data.received_quantity,
        boniu_order_no=data.bojun_order_no,
        operator=current_user.display_name,
        remark=data.remark,
    )
    db.add(inbound_rec)

    db.commit()
    db.refresh(record)
    return record


@router.get("/")
def list_purchases(
    bojun_order_no: Optional[str] = None,
    goods_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(PurchaseInbound)
    if bojun_order_no:
        query = query.filter(PurchaseInbound.bojun_order_no == bojun_order_no)
    if goods_id:
        query = query.filter(PurchaseInbound.goods_id == goods_id)
    records = query.order_by(PurchaseInbound.created_at.desc()).limit(200).all()
    result = []
    for r in records:
        goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
        result.append({
            "id": r.id,
            "bojun_order_no": r.bojun_order_no,
            "goods_id": r.goods_id,
            "goods_name": goods.name if goods else "",
            "goods_barcode": goods.barcode if goods else "",
            "received_quantity": r.received_quantity,
            "operator": r.operator,
            "remark": r.remark,
            "created_at": r.created_at,
        })
    return result


@router.get("/summary")
def get_summary(
    bojun_order_no: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """按伯俊单号汇总入库情况"""
    query = db.query(
        PurchaseInbound.bojun_order_no,
        PurchaseInbound.goods_id,
        func.sum(PurchaseInbound.received_quantity).label("total_received"),
        func.count(PurchaseInbound.id).label("times"),
    )
    if bojun_order_no:
        query = query.filter(PurchaseInbound.bojun_order_no == bojun_order_no)
    query = query.group_by(PurchaseInbound.bojun_order_no, PurchaseInbound.goods_id)
    results = []
    for row in query.all():
        goods = db.query(Goods).filter(Goods.id == row.goods_id).first()
        results.append({
            "bojun_order_no": row.bojun_order_no,
            "goods_id": row.goods_id,
            "goods_name": goods.name if goods else "",
            "total_received": int(row.total_received),
            "times": int(row.times),
        })
    return results
