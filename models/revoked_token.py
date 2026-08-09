from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from utils.database import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    jti = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    user_id = Column(
        String(100),
        nullable=False,
        index=True,
    )

    revoked_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )