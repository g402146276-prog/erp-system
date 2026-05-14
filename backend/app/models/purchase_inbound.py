from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class PurchaseInbound(Base):
    """采购入库 - 总仓来货记录，支持分批到货追踪"""
    __tablename__ = "purchase_inbounds"

    id = Column(Integer, primary_key=True, index=True)
    bojun_order_no = Column(String(50), nullable=False, index=True)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False)
    received_quantity = Column(Integer, nullable=False)
    operator = Column(String(50), nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
