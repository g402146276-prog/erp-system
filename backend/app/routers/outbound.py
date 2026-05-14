from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import update as sa_update
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.outbound_order import OutboundOrder
from app.models.goods import Goods
from app.models.warehouse import Warehouse
from app.models.stock import Stock
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/outbound", tags=["出库单"])


class OutboundCreate(BaseModel):
    order_type: str  # sales / gift / other
    goods_id: int
    quantity: int
    warehouse_id: int
    pickup_status: str = "picked_up"  # picked_up / stored
    bojun_status: str = "unknown"  # outbound / unknown / pending
    salesperson_id: Optional[int] = None
    gift_recipient: Optional[str] = None
    related_intransit_id: Optional[int] = None
    related_transfer_id: Optional[int] = None
    remark: Optional[str] = None


class OutboundUpdate(BaseModel):
    pickup_status: Optional[str] = None
    bojun_status: Optional[str] = None
    remark: Optional[str] = None


def generate_outbound_no(db: Session) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    prefix = f"CK{date_str}"
    last = db.query(OutboundOrder).filter(
        OutboundOrder.outbound_no.like(f"{prefix}%")
    ).order_by(OutboundOrder.id.desc()).first()
    if last:
        seq = int(last.outbound_no[-4:]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


@router.post("/")
def create_outbound(
    data: OutboundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建出库单，扣减库存"""
    outbound_no = generate_outbound_no(db)

    # 原子化扣减库存：在同一个 SQL 语句中检查并扣减
    result = db.execute(
        sa_update(Stock)
        .where(Stock.warehouse_id == data.warehouse_id)
        .where(Stock.goods_id == data.goods_id)
        .where(Stock.quantity >= data.quantity)
        .values(quantity=Stock.quantity - data.quantity)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail="库存不足")

    order = OutboundOrder(
        outbound_no=outbound_no,
        order_type=data.order_type,
        goods_id=data.goods_id,
        quantity=data.quantity,
        warehouse_id=data.warehouse_id,
        pickup_status=data.pickup_status,
        bojun_status=data.bojun_status,
        salesperson_id=data.salesperson_id,
        gift_recipient=data.gift_recipient,
        related_intransit_id=data.related_intransit_id,
        related_transfer_id=data.related_transfer_id,
        operator=current_user.display_name,
        remark=data.remark,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/")
def list_outbound(
    order_type: Optional[str] = None,
    pickup_status: Optional[str] = None,
    bojun_status: Optional[str] = None,
    salesperson_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(OutboundOrder)
    if order_type:
        query = query.filter(OutboundOrder.order_type == order_type)
    if pickup_status:
        query = query.filter(OutboundOrder.pickup_status == pickup_status)
    if bojun_status:
        query = query.filter(OutboundOrder.bojun_status == bojun_status)
    if salesperson_id:
        query = query.filter(OutboundOrder.salesperson_id == salesperson_id)
    records = query.order_by(OutboundOrder.created_at.desc()).limit(200).all()
    result = []
    for r in records:
        goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
        wh = db.query(Warehouse).filter(Warehouse.id == r.warehouse_id).first()
        sp = db.query(User).filter(User.id == r.salesperson_id).first() if r.salesperson_id else None
        result.append({
            "id": r.id,
            "outbound_no": r.outbound_no,
            "order_type": r.order_type,
            "goods_name": goods.name if goods else "",
            "goods_barcode": goods.barcode if goods else "",
            "quantity": r.quantity,
            "warehouse_name": wh.name if wh else "",
            "pickup_status": r.pickup_status,
            "bojun_status": r.bojun_status,
            "salesperson": sp.display_name if sp else "",
            "gift_recipient": r.gift_recipient,
            "operator": r.operator,
            "remark": r.remark,
            "created_at": r.created_at,
        })
    return result


@router.get("/{outbound_id}")
def get_outbound(outbound_id: int, db: Session = Depends(get_db)):
    r = db.query(OutboundOrder).filter(OutboundOrder.id == outbound_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="出库单不存在")
    goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
    wh = db.query(Warehouse).filter(Warehouse.id == r.warehouse_id).first()
    sp = db.query(User).filter(User.id == r.salesperson_id).first() if r.salesperson_id else None
    return {
        "id": r.id,
        "outbound_no": r.outbound_no,
        "order_type": r.order_type,
        "goods_id": r.goods_id,
        "goods_name": goods.name if goods else "",
        "goods_barcode": goods.barcode if goods else "",
        "quantity": r.quantity,
        "warehouse_id": r.warehouse_id,
        "warehouse_name": wh.name if wh else "",
        "pickup_status": r.pickup_status,
        "bojun_status": r.bojun_status,
        "salesperson_id": r.salesperson_id,
        "salesperson": sp.display_name if sp else "",
        "gift_recipient": r.gift_recipient,
        "related_intransit_id": r.related_intransit_id,
        "related_transfer_id": r.related_transfer_id,
        "operator": r.operator,
        "remark": r.remark,
        "created_at": r.created_at,
    }


@router.put("/{outbound_id}")
def update_outbound(
    outbound_id: int,
    data: OutboundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(OutboundOrder).filter(OutboundOrder.id == outbound_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="出库单不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(order, k, v)
    db.commit()
    return order


@router.put("/{outbound_id}/reverse")
def reverse_outbound(outbound_id: int, db: Session = Depends(get_db)):
    """红冲出库单，恢复库存"""
    order = db.query(OutboundOrder).filter(OutboundOrder.id == outbound_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="出库单不存在")

    # 恢复库存
    stock = db.query(Stock).filter(
        Stock.warehouse_id == order.warehouse_id,
        Stock.goods_id == order.goods_id,
    ).first()
    if stock:
        stock.quantity += order.quantity

    db.delete(order)
    db.commit()
    return {"message": "已红冲出库单"}
