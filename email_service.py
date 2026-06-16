from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),

    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,

    MAIL_SSL_TLS=True,
    MAIL_STARTTLS=False,

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

Your electricity bill has been generated.

Meter Number: {meter_no}
Amount: ₹{amount}

Please find attached bill PDF.
""",
        subtype="plain",
        attachments=[pdf_file]
    )

    print("MAIL_USERNAME =", os.getenv("MAIL_USERNAME"))
    print("MAIL_PASSWORD EXISTS =", bool(os.getenv("MAIL_PASSWORD")))

    fm = FastMail(conf)

    await fm.send_message(message)