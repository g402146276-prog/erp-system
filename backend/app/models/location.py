from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class StorageLocation(Base):
    __tablename__ = "storage_locations"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="所属仓库")
    code = Column(String(50), nullable=False, comment="货位编码 如 A-01-03")
    name = Column(String(100), nullable=True, comment="货位名称")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GoodsLocation(Base):
    __tablename__ = "goods_locations"

    id = Column(Integer, primary_key=True, index=True)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, comment="商品ID")
    location_id = Column(Integer, ForeignKey("storage_locations.id"), nullable=False, comment="货位ID")
    quantity = Column(Integer, default=0, comment="该货位上的数量")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
