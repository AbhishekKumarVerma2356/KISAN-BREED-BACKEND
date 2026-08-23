from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UUID,
)
from sqlalchemy.sql import func

from utils.database import Base


class Review(Base):
    __tablename__ = "reviews"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =========================================================
    # PRODUCT
    # =========================================================

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # =========================================================
    # USER
    # =========================================================

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # =========================================================
    # CUSTOMER NAME
    # Saved at review creation time
    # =========================================================

    customer_name = Column(
        String(200),
        nullable=False,
    )

    # =========================================================
    # RATING
    # =========================================================

    rating = Column(
        Integer,
        nullable=False,
    )

    # =========================================================
    # TITLE
    # =========================================================

    title = Column(
        String(200),
        nullable=False,
    )

    # =========================================================
    # CONTENT
    # =========================================================

    content = Column(
        Text,
        nullable=False,
    )

    # =========================================================
    # REVIEW IMAGE
    # =========================================================

    image = Column(
        String(500),
        nullable=True,
    )

    # =========================================================
    # VERIFIED REVIEW
    # =========================================================

    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # =========================================================
    # ACTIVE
    # =========================================================

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    # =========================================================
    # CREATED
    # =========================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =========================================================
    # UPDATED
    # =========================================================

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # =========================================================
    # CONSTRAINTS
    # =========================================================

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_review_rating",
        ),
    )