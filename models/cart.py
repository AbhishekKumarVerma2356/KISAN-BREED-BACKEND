import uuid

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from utils.database import Base


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(Integer, default=1)