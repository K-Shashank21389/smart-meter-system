from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_SERVER="smtp-relay.brevo.com",
    MAIL_PORT=587,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_bill_email(
    email,
    meter_no,
    amount,
    pdf_file
):
    message = MessageSchema(
        subject="Electricity Bill",
        recipients=[email],
        body=f"""
Dear Consumer,

Meter Number: {meter_no}
Amount: ₹{amount}
""",
        subtype="plain",
        attachments=[pdf_file]
    )

    fm = FastMail(conf)
    await fm.send_message(message)