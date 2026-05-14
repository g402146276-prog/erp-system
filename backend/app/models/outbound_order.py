from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class OutboundOrder(Base):
    """出库单 - 统一销售出库/赠送出库/其他出库，含提货状态和伯俊状态"""
    __tablename__ = "outbound_orders"

    id = Column(Integer, primary_key=True, index=True)
    outbound_no = Column(String(50), unique=True, nullable=False)  # CK+时间戳
    order_type = Column(String(20), nullable=False)  # sales / gift / other
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    # 出库未取追踪
    pickup_status = Column(String(20), default="picked_up")  # picked_up / stored
    # 伯俊出库状态
    bojun_status = Column(String(20), default="unknown")  # outbound / unknown / pending
    # 关联
    salesperson_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_intransit_id = Column(Integer, ForeignKey("intransit_orders.id"), nullable=True)
    related_transfer_id = Column(Integer, ForeignKey("transfer_applies.id"), nullable=True)
    # 赠品专用
    gift_recipient = Column(String(100), nullable=True)
    operator = Column(String(50), nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
