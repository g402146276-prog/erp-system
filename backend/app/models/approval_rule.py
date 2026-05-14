from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class ApprovalRule(Base):
    """审批规则 - 灵活配置调拨审批流程"""
    __tablename__ = "approval_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    priority = Column(Integer, default=0)
    # 条件（为空表示"任意"）
    source_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    dest_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    transfer_type = Column(String(20), nullable=True)  # move / borrow / damage
    # 动作
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
