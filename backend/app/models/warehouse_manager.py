from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base


class WarehouseManager(Base):
    __tablename__ = "warehouse_managers"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("warehouse_id", "user_id", name="uq_warehouse_user"),
    )
