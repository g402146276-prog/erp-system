from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from app.database import get_db
from app.models.transfer_apply import TransferApply
from app.models.transfer import TransferRecord
from app.models.goods import Goods
from app.models.warehouse import Warehouse
from app.models.stock import Stock
from app.models.user import User
from app.models.approval_rule import ApprovalRule
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/transfer-apply", tags=["调拨申请单"])


class TransferApplyCreate(BaseModel):
    transfer_type: str  # move / borrow / damage
    source_warehouse_id: int
    dest_warehouse_id: int
    goods_id: int
    quantity: int
    reason: Optional[str] = None


class TransferApplyApprove(BaseModel):
    approve: bool  # True=通过, False=拒绝
    reject_reason: Optional[str] = None


def generate_apply_no(db: Session) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    prefix = f"DB{date_str}"
    last = db.query(TransferApply).filter(
        TransferApply.apply_no.like(f"{prefix}%")
    ).order_by(TransferApply.id.desc()).first()
    if last:
        seq = int(last.apply_no[-4:]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


def resolve_approver(source_wh: int, dest_wh: int, ttype: str, db: Session):
    rules = db.query(ApprovalRule).filter(
        ApprovalRule.is_active == True
    ).order_by(ApprovalRule.priority).all()
    for rule in rules:
        if rule.source_warehouse_id is not None and rule.source_warehouse_id != source_wh:
            continue
        if rule.dest_warehouse_id is not None and rule.dest_warehouse_id != dest_wh:
            continue
        if rule.transfer_type is not None and rule.transfer_type != ttype:
            continue
        return rule.approver_id
    return None


@router.post("/")
def create_apply(
    data: TransferApplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    apply_no = generate_apply_no(db)
    approver_id = resolve_approver(
        data.source_warehouse_id, data.dest_warehouse_id, data.transfer_type, db
    )
    status = "pending" if approver_id else "draft"

    apply = TransferApply(
        apply_no=apply_no,
        transfer_type=data.transfer_type,
        source_warehouse_id=data.source_warehouse_id,
        dest_warehouse_id=data.dest_warehouse_id,
        goods_id=data.goods_id,
        quantity=data.quantity,
        applicant_id=current_user.id,
        approver_id=approver_id,
        status=status,
        reason=data.reason,
        operator=current_user.display_name,
    )
    db.add(apply)
    db.commit()
    db.refresh(apply)
    return apply


@router.get("/")
def list_applies(
    status: Optional[str] = None,
    transfer_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(TransferApply)
    if status:
        query = query.filter(TransferApply.status == status)
    if transfer_type:
        query = query.filter(TransferApply.transfer_type == transfer_type)
    records = query.order_by(TransferApply.created_at.desc()).limit(200).all()
    result = []
    for r in records:
        goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
        src_wh = db.query(Warehouse).filter(Warehouse.id == r.source_warehouse_id).first()
        dst_wh = db.query(Warehouse).filter(Warehouse.id == r.dest_warehouse_id).first()
        applicant = db.query(User).filter(User.id == r.applicant_id).first()
        result.append({
            "id": r.id,
            "apply_no": r.apply_no,
            "transfer_type": r.transfer_type,
            "source_warehouse_name": src_wh.name if src_wh else "",
            "dest_warehouse_name": dst_wh.name if dst_wh else "",
            "goods_name": goods.name if goods else "",
            "goods_barcode": goods.barcode if goods else "",
            "quantity": r.quantity,
            "applicant": applicant.display_name if applicant else "",
            "approver_id": r.approver_id,
            "status": r.status,
            "reason": r.reason,
            "reject_reason": r.reject_reason,
            "operator": r.operator,
            "created_at": r.created_at,
            "approved_at": r.approved_at,
        })
    return result


@router.get("/{apply_id}")
def get_apply(apply_id: int, db: Session = Depends(get_db)):
    r = db.query(TransferApply).filter(TransferApply.id == apply_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="调拨申请不存在")
    goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
    src_wh = db.query(Warehouse).filter(Warehouse.id == r.source_warehouse_id).first()
    dst_wh = db.query(Warehouse).filter(Warehouse.id == r.dest_warehouse_id).first()
    applicant = db.query(User).filter(User.id == r.applicant_id).first()
    return {
        "id": r.id,
        "apply_no": r.apply_no,
        "transfer_type": r.transfer_type,
        "source_warehouse_id": r.source_warehouse_id,
        "source_warehouse_name": src_wh.name if src_wh else "",
        "dest_warehouse_id": r.dest_warehouse_id,
        "dest_warehouse_name": dst_wh.name if dst_wh else "",
        "goods_id": r.goods_id,
        "goods_name": goods.name if goods else "",
        "goods_barcode": goods.barcode if goods else "",
        "quantity": r.quantity,
        "applicant_id": r.applicant_id,
        "applicant": applicant.display_name if applicant else "",
        "approver_id": r.approver_id,
        "status": r.status,
        "reason": r.reason,
        "reject_reason": r.reject_reason,
        "operator": r.operator,
        "created_at": r.created_at,
        "approved_at": r.approved_at,
    }


@router.put("/{apply_id}/approve")
def approve_apply(
    apply_id: int,
    data: TransferApplyApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    apply = db.query(TransferApply).filter(TransferApply.id == apply_id).first()
    if not apply:
        raise HTTPException(status_code=404, detail="调拨申请不存在")
    if apply.status != "pending":
        raise HTTPException(status_code=400, detail="只能审批待审批的申请")

    if data.approve:
        # 检查库存是否足够
        if apply.transfer_type in ("move", "borrow", "damage"):
            stock = db.query(Stock).filter(
                Stock.warehouse_id == apply.source_warehouse_id,
                Stock.goods_id == apply.goods_id,
            ).first()
            if not stock or stock.quantity < apply.quantity:
                raise HTTPException(status_code=400, detail="调出仓库库存不足")

        apply.status = "approved"
        apply.approved_at = datetime.now()
        apply.approver_id = current_user.id

        # 移库类型：执行库存移动
        if apply.transfer_type == "move":
            src_stock = db.query(Stock).filter(
                Stock.warehouse_id == apply.source_warehouse_id,
                Stock.goods_id == apply.goods_id,
            ).first()
            if src_stock:
                src_stock.quantity -= apply.quantity

            dst_stock = db.query(Stock).filter(
                Stock.warehouse_id == apply.dest_warehouse_id,
                Stock.goods_id == apply.goods_id,
            ).first()
            if dst_stock:
                dst_stock.quantity += apply.quantity
            else:
                dst_stock = Stock(
                    warehouse_id=apply.dest_warehouse_id,
                    goods_id=apply.goods_id,
                    quantity=apply.quantity,
                )
                db.add(dst_stock)

        # 借样/报损类型：仅减少源仓库库存
        if apply.transfer_type in ("borrow", "damage"):
            src_stock = db.query(Stock).filter(
                Stock.warehouse_id == apply.source_warehouse_id,
                Stock.goods_id == apply.goods_id,
            ).first()
            if src_stock:
                src_stock.quantity -= apply.quantity

    else:
        apply.status = "rejected"
        apply.reject_reason = data.reject_reason

    db.commit()
    return apply


@router.put("/{apply_id}/complete")
def complete_apply(apply_id: int, db: Session = Depends(get_db)):
    """借样归还或报损完成：将状态标记为已完成"""
    apply = db.query(TransferApply).filter(TransferApply.id == apply_id).first()
    if not apply:
        raise HTTPException(status_code=404, detail="调拨申请不存在")
    if apply.status not in ("approved",):
        raise HTTPException(status_code=400, detail="只能完成已审批的申请")
    apply.status = "completed"
    db.commit()
    return apply


@router.put("/{apply_id}/cancel")
def cancel_apply(apply_id: int, db: Session = Depends(get_db)):
    apply = db.query(TransferApply).filter(TransferApply.id == apply_id).first()
    if not apply:
        raise HTTPException(status_code=404, detail="调拨申请不存在")
    if apply.status in ("completed", "cancelled", "rejected"):
        raise HTTPException(status_code=400, detail="当前状态不可作废")

    # 如果已审批通过，需要恢复库存
    if apply.status == "approved":
        if apply.transfer_type == "move":
            # 恢复源仓库库存
            src_stock = db.query(Stock).filter(
                Stock.warehouse_id == apply.source_warehouse_id,
                Stock.goods_id == apply.goods_id,
            ).first()
            if src_stock:
                src_stock.quantity += apply.quantity
            # 扣减目标仓库库存
            dst_stock = db.query(Stock).filter(
                Stock.warehouse_id == apply.dest_warehouse_id,
                Stock.goods_id == apply.goods_id,
            ).first()
            if dst_stock:
                dst_stock.quantity = max(0, dst_stock.quantity - apply.quantity)

        if apply.transfer_type in ("borrow", "damage"):
            # 归还源仓库库存
            src_stock = db.query(Stock).filter(
                Stock.warehouse_id == apply.source_warehouse_id,
                Stock.goods_id == apply.goods_id,
            ).first()
            if src_stock:
                src_stock.quantity += apply.quantity

    apply.status = "cancelled"
    db.commit()
    return apply
