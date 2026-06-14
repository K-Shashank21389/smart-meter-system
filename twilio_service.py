from twilio.rest import Client
from dotenv import load_dotenv


load_dotenv()

import os

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
VERIFY_SERVICE_SID = "VA186fd35443fe74bff71eb5b86c2d606a"

client = Client(
    ACCOUNT_SID,
    AUTH_TOKEN
)


def send_otp(phone_number):

    verification = client.verify.v2.services(
        VERIFY_SERVICE_SID
    ).verifications.create(
        to=phone_number,
        channel="sms"
    )

    return verification.status


def verify_otp(phone_number, otp):

    verification_check = client.verify.v2.services(
        VERIFY_SERVICE_SID
    ).verification_checks.create(
        to=phone_number,
        code=otp
    )

    return verification_check.status