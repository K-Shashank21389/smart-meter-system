import requests
import os

async def send_bill_email(
    email,
    meter_no,
    amount
):
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "email": os.getenv("MAIL_FROM")
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "Electricity Bill",
        "htmlContent": f"""
        <h2>Electricity Bill</h2>

        <p>Meter Number: {meter_no}</p>

        <p>Amount: ₹{amount}</p>
        """
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers=headers,
        json=payload
    )

    print(response.status_code)
    print(response.text)