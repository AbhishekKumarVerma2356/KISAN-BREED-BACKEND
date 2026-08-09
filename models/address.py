from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from utils.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    address_type = Column(
        String(20),
        nullable=False,
    )

    flat_house_no = Column(
        String(100),
        nullable=False,
    )

    address1 = Column(
        String(255),
        nullable=False,
    )

    address2 = Column(
        String(255),
        nullable=True,
    )

    state = Column(
        String(100),
        nullable=False,
    )

    city_village = Column(
        String(150),
        nullable=False,
    )

    pincode = Column(
        String(10),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="addresses",
    )