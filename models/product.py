from sqlalchemy import Column, Integer, Numeric, String, Float, Text
from utils.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    slug = Column(
        String(200),
        unique=True,
        nullable=False
    )

    category = Column(
        String(100),
        nullable=True
    )

    short_description = Column(
        Text,
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    price = Column(
        Float,
        nullable=True
    )

    discount = Column(
        Numeric(5, 2),
        default=0,
        nullable=False
    )

    image = Column(
        String(255),
        nullable=True
    )

    # =========================================================
    # PRODUCT QUANTITY
    # =========================================================

    quantity = Column(
        Numeric(10, 2),
        nullable=False,
        default=1
    )

    # =========================================================
    # UNIT OF MEASURE
    # Example: kg, gram, litre, ml, piece, packet, etc.
    # =========================================================

    unit_of_measure = Column(
        String(50),
        nullable=False,
        default="piece"
    )