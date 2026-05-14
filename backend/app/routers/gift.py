from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models.outbound_order import OutboundOrder
from app.models.goods import Goods
from app.models.warehouse import Warehouse
from app.models.user import User

router = APIRouter(prefix="/api/gift", tags=["赠送单"])


@router.get("/")
def list_gifts(
    pickup_status: Optional[str] = None,
    bojun_status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """查询赠送单（出库单中 type=gift 的记录）"""
    query = db.query(OutboundOrder).filter(OutboundOrder.order_type == "gift")
    if pickup_status:
        query = query.filter(OutboundOrder.pickup_status == pickup_status)
    if bojun_status:
        query = query.filter(OutboundOrder.bojun_status == bojun_status)
    records = query.order_by(OutboundOrder.created_at.desc()).limit(200).all()
    result = []
    for r in records:
        goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
        wh = db.query(Warehouse).filter(Warehouse.id == r.warehouse_id).first()
        result.append({
            "id": r.id,
            "outbound_no": r.outbound_no,
            "goods_name": goods.name if goods else "",
            "goods_barcode": goods.barcode if goods else "",
            "quantity": r.quantity,
            "warehouse_name": wh.name if wh else "",
            "pickup_status": r.pickup_status,
            "bojun_status": r.bojun_status,
            "gift_recipient": r.gift_recipient,
            "operator": r.operator,
            "remark": r.remark,
            "created_at": r.created_at,
        })
    return result


@router.get("/summary")
def gift_summary(db: Session = Depends(get_db)):
    """赠送单汇总统计"""
    total = db.query(OutboundOrder).filter(OutboundOrder.order_type == "gift").count()
    pending = db.query(OutboundOrder).filter(
        OutboundOrder.order_type == "gift",
        OutboundOrder.bojun_status == "pending",
    ).count()
    synced = db.query(OutboundOrder).filter(
        OutboundOrder.order_type == "gift",
        OutboundOrder.bojun_status == "outbound",
    ).count()
    return {
        "total": total,
        "pending_bojun": pending,
        "synced_bojun": synced,
    }


@router.get("/reconciliation")
def gift_reconciliation(goods_id: int, db: Session = Depends(get_db)):
    """查询某商品在赠送单中的待核销数量"""
    result = db.query(
        OutboundOrder.goods_id,
        OutboundOrder.bojun_status,
        func.sum(OutboundOrder.quantity).label("total_qty"),
    ).filter(
        OutboundOrder.order_type == "gift",
        OutboundOrder.goods_id == goods_id,
    ).group_by(
        OutboundOrder.goods_id, OutboundOrder.bojun_status
    ).all()
    goods = db.query(Goods).filter(Goods.id == goods_id).first()
    data = {"goods_name": goods.name if goods else "", "goods_barcode": goods.barcode if goods else ""}
    for row in result:
        data[f"bojun_{row.bojun_status}_qty"] = int(row.total_qty)
    if "bojun_pending_qty" not in data:
        data["bojun_pending_qty"] = 0
    if "bojun_outbound_qty" not in data:
        data["bojun_outbound_qty"] = 0
    if "bojun_unknown_qty" not in data:
        data["bojun_unknown_qty"] = 0
    return data
