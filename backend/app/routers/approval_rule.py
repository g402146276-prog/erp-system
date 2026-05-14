from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.approval_rule import ApprovalRule
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/approval-rules", tags=["审批规则"])


class RuleCreate(BaseModel):
    name: str
    priority: int = 0
    source_warehouse_id: Optional[int] = None
    dest_warehouse_id: Optional[int] = None
    transfer_type: Optional[str] = None
    approver_id: int
    remark: Optional[str] = None


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    priority: Optional[int] = None
    source_warehouse_id: Optional[int] = None
    dest_warehouse_id: Optional[int] = None
    transfer_type: Optional[str] = None
    approver_id: Optional[int] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = None


@router.get("/")
def list_rules(db: Session = Depends(get_db)):
    rules = db.query(ApprovalRule).order_by(ApprovalRule.priority).all()
    return rules


@router.post("/")
def create_rule(
    data: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可配置审批规则")
    rule = ApprovalRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/{rule_id}")
def update_rule(
    rule_id: int,
    data: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可配置审批规则")
    rule = db.query(ApprovalRule).filter(ApprovalRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(rule, k, v)
    db.commit()
    return rule


@router.delete("/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可配置审批规则")
    rule = db.query(ApprovalRule).filter(ApprovalRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(rule)
    db.commit()
    return {"message": "已删除"}


@router.post("/resolve")
def resolve_approver(
    source_warehouse_id: int,
    dest_warehouse_id: int,
    transfer_type: str,
    db: Session = Depends(get_db),
):
    """根据规则匹配审批人"""
    rules = db.query(ApprovalRule).filter(
        ApprovalRule.is_active == True
    ).order_by(ApprovalRule.priority).all()

    for rule in rules:
        if rule.source_warehouse_id is not None and rule.source_warehouse_id != source_warehouse_id:
            continue
        if rule.dest_warehouse_id is not None and rule.dest_warehouse_id != dest_warehouse_id:
            continue
        if rule.transfer_type is not None and rule.transfer_type != transfer_type:
            continue
        return {"approver_id": rule.approver_id, "rule_name": rule.name}

    return {"approver_id": None, "rule_name": None}
