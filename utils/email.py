import os
import smtplib

from dotenv import load_dotenv

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_password_reset_otp(
    recipient_email: str,
    otp: str,
):

    subject = "Kisan Breed - Password Reset OTP"

    body = f"""
Hello,

We received a request to reset your Kisan Breed account password.

Your 6-digit OTP is:

{otp}

This OTP is valid for a limited time.

If you did not request this password reset, please ignore this email.

Regards,
Kisan Breed Team
"""

    message = MIMEMultipart()

    message["From"] = SMTP_USERNAME
    message["To"] = recipient_email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    try:

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            server.sendmail(
                SMTP_USERNAME,
                recipient_email,
                message.as_string(),
            )

    except Exception as error:

        print(
            "PASSWORD RESET EMAIL ERROR:",
            error,
        )

        raise