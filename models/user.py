import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from utils.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    full_name = Column(
        String(150),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    contact_number = Column(
        String(15),
        nullable=False,
    )

    alternate_contact_number = Column(
        String(15),
        nullable=True,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        String(20),
        nullable=False,
        default="customer",
    )

    addresses = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan",
    )