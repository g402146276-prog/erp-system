from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    hashed_password = Column(String(200), nullable=False, comment="密码哈希")
    display_name = Column(String(50), nullable=False, comment="显示名称")
    role = Column(String(20), default="staff", comment="admin/manager/staff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
