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
from app.models.intransit_order import IntransitOrder
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/purchase-inbound", tags=["采购入库"])


class PurchaseCreate(BaseModel):
    bojun_order_no: str
    goods_id: int
    received_quantity: int
    warehouse_id: int
    remark: Optional[str] = None


class BatchItem(BaseModel):
    goods_id: int
    received_quantity: int
    bojun_order_no: str = ""
    remark: Optional[str] = None


class BatchCreate(BaseModel):
    warehouse_id: int
    items: List[BatchItem]
    intransit_order_id: Optional[int] = None


def _do_create(data, db, operator):
    """创建一条采购入库记录 + 更新库存 + 写入入库记录"""
    record = PurchaseInbound(
        bojun_order_no=data.bojun_order_no,
        warehouse_id=data.warehouse_id,
        goods_id=data.goods_id,
        received_quantity=data.received_quantity,
        operator=operator,
        remark=data.remark,
    )
    db.add(record)

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

    inbound_rec = InboundRecord(
        warehouse_id=data.warehouse_id,
        goods_id=data.goods_id,
        quantity=data.received_quantity,
        boniu_order_no=data.bojun_order_no,
        operator=operator,
        remark=data.remark,
    )
    db.add(inbound_rec)
    return record


@router.post("/")
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """记录一次采购入库，同时增加库存"""
    record = _do_create(data, db, current_user.display_name)
    db.commit()
    db.refresh(record)
    return record


@router.post("/batch")
def batch_create_purchase(
    data: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量记录采购入库（同一仓库，每条记录独立伯俊单号）"""
    records = []
    for item in data.items:
        if not item.bojun_order_no:
            raise HTTPException(status_code=400, detail=f"第{len(records)+1}行缺少伯俊单号")
        wrapper = PurchaseCreate(
            bojun_order_no=item.bojun_order_no,
            goods_id=item.goods_id,
            received_quantity=item.received_quantity,
            warehouse_id=data.warehouse_id,
            remark=item.remark,
        )
        rec = _do_create(wrapper, db, current_user.display_name)
        records.append(rec)
    # 如果关联了在途订单，自动标记为已完成（同一事务）
    if data.intransit_order_id:
        order = db.query(IntransitOrder).filter(
            IntransitOrder.id == data.intransit_order_id,
            IntransitOrder.status == "pending",
        ).first()
        if order:
            order.status = "completed"

    db.commit()
    for r in records:
        db.refresh(r)

    return {"message": f"批量入库完成，共{len(records)}项", "count": len(records)}


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
            "warehouse_id": r.warehouse_id,
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
