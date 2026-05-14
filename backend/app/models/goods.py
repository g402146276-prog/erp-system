from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Goods(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(50), unique=True, index=True, nullable=False, comment="商品条码")
    name = Column(String(100), nullable=False, comment="商品名称")
    spec = Column(String(100), comment="规格型号")
    unit = Column(String(20), default="个", comment="计量单位")
    category = Column(String(50), comment="分类")
    price = Column(Float, default=0, comment="单价")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
