import asyncio
from email_service import send_bill_email

asyncio.run(
    send_bill_email(
        email="shashankkunduru49@gmail.com",
        meter_no="240069381738",
        amount=771.88,
        pdf_file="240069381738_bill.pdf",
        attachments=[pdf_file]
    )
)

print("Email Sent")