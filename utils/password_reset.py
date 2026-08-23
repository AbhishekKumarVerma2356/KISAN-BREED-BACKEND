import hashlib
import secrets
from datetime import datetime, timedelta, timezone


OTP_EXPIRY_MINUTES = 10


def generate_otp() -> str:
    """
    Generate a secure 6 digit OTP.
    """
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    """
    Hash OTP before storing it in database.
    """
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def verify_otp(
    otp: str,
    otp_hash: str,
) -> bool:
    """
    Verify plain OTP against stored hash.
    """
    return secrets.compare_digest(
        hash_otp(otp),
        otp_hash,
    )


def get_otp_expiry() -> datetime:
    """
    OTP expires after 10 minutes.
    """
    return datetime.now(timezone.utc) + timedelta(
        minutes=OTP_EXPIRY_MINUTES
    )