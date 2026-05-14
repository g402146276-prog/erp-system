from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models.goods import Goods
from app.models.stock import Stock
from app.models.outbound_order import OutboundOrder
from app.models.transfer_apply import TransferApply

router = APIRouter(prefix="/api/reconciliation", tags=["对账看板"])


@router.get("/")
def reconciliation(
    goods_id: Optional[int] = None,
    barcode: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    对账看板 - 展示伯俊 vs 实物 vs 各项差异

    公式: 伯俊库存 = 实物库存 + 赠送待核销 + 借出未还 + 空吊数据 - 出库未取(伯俊已出库)
    """
    query = db.query(Goods)
    if goods_id:
        query = query.filter(Goods.id == goods_id)
    if barcode:
        query = query.filter(Goods.barcode == barcode)

    goods_list = query.order_by(Goods.name).all()
    results = []

    for goods in goods_list:
        # 实物库存：所有仓库总和
        physical_qty = db.query(func.coalesce(func.sum(Stock.quantity), 0)).filter(
            Stock.goods_id == goods.id
        ).scalar()

        # 赠送待核销：赠送单中伯俊未出库的
        gift_pending_qty = db.query(func.coalesce(func.sum(OutboundOrder.quantity), 0)).filter(
            OutboundOrder.goods_id == goods.id,
            OutboundOrder.order_type == "gift",
            OutboundOrder.bojun_status == "pending",
        ).scalar()

        # 赠送已同步（伯俊已出库）
        gift_synced_qty = db.query(func.coalesce(func.sum(OutboundOrder.quantity), 0)).filter(
            OutboundOrder.goods_id == goods.id,
            OutboundOrder.order_type == "gift",
            OutboundOrder.bojun_status == "outbound",
        ).scalar()

        # 借出未还：调拨类型=borrow 且已审批/已完成的
        borrowed_qty = db.query(func.coalesce(func.sum(TransferApply.quantity), 0)).filter(
            TransferApply.goods_id == goods.id,
            TransferApply.transfer_type == "borrow",
            TransferApply.status.in_(["approved", "completed"]),
        ).scalar()

        # 出库未取（暂存仓库）：出库单中 pickup_status=stored 的
        stored_qty = db.query(func.coalesce(func.sum(OutboundOrder.quantity), 0)).filter(
            OutboundOrder.goods_id == goods.id,
            OutboundOrder.pickup_status == "stored",
        ).scalar()

        # 出库未取中伯俊已出库的
        stored_bojun_out_qty = db.query(func.coalesce(func.sum(OutboundOrder.quantity), 0)).filter(
            OutboundOrder.goods_id == goods.id,
            OutboundOrder.pickup_status == "stored",
            OutboundOrder.bojun_status == "outbound",
        ).scalar()

        # 计算建议的伯俊库存
        suggested_bojun = physical_qty + gift_pending_qty + borrowed_qty - stored_bojun_out_qty

        results.append({
            "goods_id": goods.id,
            "goods_name": goods.name,
            "goods_barcode": goods.barcode,
            "spec": goods.spec,
            "unit": goods.unit,
            "physical_stock": int(physical_qty),
            "gift_pending": int(gift_pending_qty),
            "gift_synced": int(gift_synced_qty),
            "borrowed_out": int(borrowed_qty),
            "stored_in_warehouse": int(stored_qty),
            "stored_bojun_out": int(stored_bojun_out_qty),
            "suggested_bojun": int(suggested_bojun),
        })

    return results


@router.get("/detail/{goods_id}")
def reconciliation_detail(goods_id: int, db: Session = Depends(get_db)):
    """商品对账明细 - 列出所有相关单据"""
    goods = db.query(Goods).filter(Goods.id == goods_id).first()
    if not goods:
        return {"error": "商品不存在"}

    stocks = db.query(Stock).filter(Stock.goods_id == goods_id).all()
    stock_detail = [{"warehouse_id": s.warehouse_id, "quantity": s.quantity} for s in stocks]

    gifts = db.query(OutboundOrder).filter(
        OutboundOrder.goods_id == goods_id,
        OutboundOrder.order_type == "gift",
    ).order_by(OutboundOrder.created_at.desc()).limit(50).all()

    borrows = db.query(TransferApply).filter(
        TransferApply.goods_id == goods_id,
        TransferApply.transfer_type == "borrow",
        TransferApply.status.in_(["approved", "completed"]),
    ).order_by(TransferApply.created_at.desc()).limit(50).all()

    stored = db.query(OutboundOrder).filter(
        OutboundOrder.goods_id == goods_id,
        OutboundOrder.pickup_status == "stored",
    ).order_by(OutboundOrder.created_at.desc()).limit(50).all()

    return {
        "goods": {
            "id": goods.id,
            "name": goods.name,
            "barcode": goods.barcode,
        },
        "stocks": stock_detail,
        "gift_orders": [
            {"outbound_no": g.outbound_no, "quantity": g.quantity,
             "bojun_status": g.bojun_status, "created_at": g.created_at}
            for g in gifts
        ],
        "borrow_orders": [
            {"apply_no": b.apply_no, "quantity": b.quantity,
             "status": b.status, "created_at": b.created_at}
            for b in borrows
        ],
        "stored_orders": [
            {"outbound_no": s.outbound_no, "quantity": s.quantity,
             "bojun_status": s.bojun_status, "created_at": s.created_at}
            for s in stored
        ],
    }
