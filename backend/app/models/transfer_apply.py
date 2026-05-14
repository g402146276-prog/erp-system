from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class TransferApply(Base):
    """调拨申请单 - 统一所有内部流转，含审批流程"""
    __tablename__ = "transfer_applies"

    id = Column(Integer, primary_key=True, index=True)
    apply_no = Column(String(50), unique=True, nullable=False)  # DB+时间戳
    transfer_type = Column(String(20), nullable=False)  # move/borrow/damage
    source_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    dest_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="draft")  # draft/pending/approved/rejected/completed/cancelled
    reason = Column(Text, nullable=True)
    reject_reason = Column(Text, nullable=True)
    operator = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    approved_at = Column(DateTime, nullable=True)
