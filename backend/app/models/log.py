from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operator = Column(String(50), nullable=False, comment="操作人")
    action = Column(String(50), nullable=False, comment="操作类型: create/update/delete/approve/reverse")
    target_type = Column(String(50), nullable=False, comment="操作对象类型: goods/stock/transfer/adjustment/location")
    target_id = Column(Integer, nullable=True, comment="操作对象ID")
    detail = Column(Text, nullable=True, comment="操作详情")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
