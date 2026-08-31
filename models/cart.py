from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint
)

from sqlalchemy.dialects.postgresql import UUID

from utils.database import Base


class Cart(Base):

    __tablename__ = "cart"

    # =========================================================
    # CART ID
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================================
    # USER
    # =========================================================

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =========================================================
    # PRODUCT
    # =========================================================

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    # =========================================================
    # CART QUANTITY
    # =========================================================

    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )

    # =========================================================
    # CONSTRAINTS
    # =========================================================

    __table_args__ = (

        # Quantity must always be greater than zero
        CheckConstraint(
            "quantity > 0",
            name="check_cart_quantity_positive"
        ),

        # Same product should not appear twice
        UniqueConstraint(
            "user_id",
            "product_id",
            name="unique_user_product_cart"
        ),
    )