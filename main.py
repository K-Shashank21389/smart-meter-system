from fastapi import FastAPI
from pydantic import BaseModel
from pdf_generator import generate_pdf
from qr_generator import generate_qr
from db import get_connection
import sqlite3
from billing import calculate_bill

from fastapi.responses import FileResponse
import random
from datetime import datetime, timedelta

import jwt

from jose import jwt, JWTError
from fastapi import Header, HTTPException

from twilio_service import send_otp
from twilio_service import verify_otp

from email_service import send_bill_email
import asyncio



from anomaly_detector import detect_anomaly




from twilio_service import verify_otp as twilio_verify_otp

from twilio_service import (
    client,
    VERIFY_SERVICE_SID
)

app = FastAPI(
    title="Smart Meter API"
)

SECRET_KEY = "smart_meter_secret_key"

ALGORITHM = "HS256"

import jwt

def create_token(data: dict):

    token = jwt.encode(
        data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def verify_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

# -------------------------
# MODEL
# -------------------------

class ConsumerCreate(BaseModel):
    meter_no: str
    name: str
    mobile: str
    previous_reading: int


# -------------------------
# HOME
# -------------------------

@app.get("/")
def home():
    return {"message": "Smart Meter API Running"}


# -------------------------
# ADD CONSUMER
# -------------------------

@app.post("/consumer")
def add_consumer(consumer: ConsumerCreate):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""
                       INSERT INTO consumer(meter_no,
                                            name,
                                            mobile,
                                            previous_reading)
                       VALUES (%s, %s, %s, %s)
                       """, (
                           consumer.meter_no,
                           consumer.name,
                           consumer.mobile,
                           consumer.previous_reading
                       ))

        conn.commit()

        return {
            "message": "Consumer Added Successfully"
        }

    finally:
        conn.close()


# -------------------------
# GET ALL CONSUMERS
# -------------------------

@app.get("/consumers")
def get_consumers(
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM consumer
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


class MeterReading(BaseModel):
    meter_no: str
    current_reading: int


@app.post("/meter-reading")
def receive_reading(reading: MeterReading):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT name, previous_reading
                   FROM consumer
                   WHERE meter_no = %s
                   """, (reading.meter_no,))
    row = cursor.fetchone()

    if not row:
        conn.close()

        return {
            "error": "Consumer not found"
        }

    name = row[0]
    previous_reading = row[1]

    cursor.execute("""
                   SELECT email
                   FROM consumer
                   WHERE meter_no = %s
                   """, (reading.meter_no,))

    email = cursor.fetchone()[0]

    if not email:
        return {
            "error": "Consumer email not found"
        }

    cursor.execute("""
                   SELECT current_reading
                   FROM bills
                   WHERE meter_no = %s
                   ORDER BY id DESC LIMIT 10
                   """, (reading.meter_no,))

    rows = cursor.fetchall()

    history = [
        row[0]
        for row in rows
    ]
    is_anomaly = detect_anomaly(
        history,
        reading.current_reading
    )

    if is_anomaly:
        alert = "AI Anomaly Detected"
    else:
        alert = "Normal"

    if reading.current_reading < previous_reading:
        conn.close()

        return {
            "error": "Current reading cannot be less than previous reading"
        }

    bill = calculate_bill(
        previous_reading,
        reading.current_reading
    )

    qr_file = generate_qr(
        reading.meter_no,
        bill["bill_amount"]
    )

    pdf_file = generate_pdf(
        reading.meter_no,
        name,
        bill["units"],
        bill["bill_amount"]
    )

    try:
        asyncio.run(
            send_bill_email(
                email,
                reading.meter_no,
                bill["bill_amount"],
                pdf_file
            )
        )
        print("Email sent successfully")

    except Exception as e:
        print("Email Error:", str(e))


    cursor.execute("""
                   INSERT INTO bills(meter_no,
                                     previous_reading,
                                     current_reading,
                                     units,
                                     bill_amount,
                                     bill_date,
                                     payment_status,
                                     theft_alert)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   """, (
                       reading.meter_no,
                       previous_reading,
                       reading.current_reading,
                       bill["units"],
                       bill["bill_amount"],
                       datetime.now().strftime("%d-%m-%Y"),
                       "Pending",
                       alert
                   ))

    cursor.execute("""
                   UPDATE consumer
                   SET previous_reading=%s
                   WHERE meter_no = %s
                   """, (
        reading.current_reading,
        reading.meter_no
    ))

    conn.commit()
    conn.close()

    return {
        "meter_no": reading.meter_no,
        "units": bill["units"],
        "bill_amount": bill["bill_amount"],
        "pdf": pdf_file,
        "qr": qr_file,
        "status": "Generated"
    }


@app.get("/bill/{meter_no}")
def get_bill(
    meter_no: str,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.name,
               b.units,
               b.bill_amount
        FROM bills b
        JOIN consumer c
        ON c.meter_no = b.meter_no
        WHERE b.meter_no=%s
        ORDER BY b.id DESC
        LIMIT 1
    """, (meter_no,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    name = row[0]
    units = row[1]
    amount = row[2]

    pdf_file = generate_pdf(
        meter_no,
        name,
        units,
        amount
    )

    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename=pdf_file
    )


@app.get("/bill/{meter_no}")
def get_bill(
    meter_no: str,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.name,
               b.units,
               b.bill_amount
        FROM bills b
        JOIN consumer c
        ON c.meter_no = b.meter_no
        WHERE b.meter_no=%s
        ORDER BY b.id DESC
        LIMIT 1
    """, (meter_no,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {"error": "Bill not found"}

    name = row[0]
    units = row[1]
    amount = row[2]

    pdf_file = generate_pdf(
        meter_no,
        name,
        units,
        amount
    )

    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename=pdf_file
    )


@app.post("/pay-bill")
def pay_bill(
    payment: PaymentRequest,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bills
        SET payment_status='Paid'
        WHERE id = (
            SELECT MAX(id)
            FROM bills
            WHERE meter_no=%s
        )
        RETURNING id
    """, (payment.meter_no,))

    updated = cursor.fetchone()

    if not updated:
        conn.close()

        return {
            "error": "No Bill Found"
        }

    conn.commit()
    conn.close()

    return {
        "meter_no": payment.meter_no,
        "status": "Paid"
    }




class OTPRequest(BaseModel):
    meter_no: str


class OTPVerify(BaseModel):
    meter_no: str
    otp: str


@app.get("/consumer-bills/{meter_no}")
def consumer_bills(
    meter_no: str,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        bill_date,
        units,
        bill_amount,
        payment_status
    FROM bills
    WHERE meter_no=%s
    ORDER BY id DESC
    """, (meter_no,))

    rows = cursor.fetchall()

    conn.close()

    return rows


@app.get("/dashboard")
def dashboard(
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM consumer
    """)
    total_consumers = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM bills
    """)
    total_bills = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM bills
    WHERE payment_status='Paid'
    """)
    paid_bills = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM bills
    WHERE payment_status='Pending'
    """)
    pending_bills = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COALESCE(
        SUM(bill_amount),
        0
    )
    FROM bills
    WHERE payment_status='Paid'
    """)
    revenue = cursor.fetchone()[0]

    conn.close()

    return {
        "total_consumers": total_consumers,
        "total_bills": total_bills,
        "paid_bills": paid_bills,
        "pending_bills": pending_bills,
        "revenue": float(revenue)
    }

@app.post("/send-otp")
def send_otp_api(data: OTPRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mobile
        FROM consumer
        WHERE meter_no=%s
    """, (data.meter_no,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {"error": "Meter not found"}

    mobile = str(row[0])

    status = send_otp(mobile)

    print("MOBILE FROM DB =", mobile)

    return {
        "status": status
    }

@app.post("/verify-otp")
def verify_otp_api(data: OTPVerify):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT mobile
        FROM consumer
        WHERE meter_no=%s
        """,
        (data.meter_no,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {"login": "failed"}

    mobile = str(row[0])

    status = verify_otp(
        mobile,
        data.otp
    )

    if status == "approved":

        token = create_token(
            {"meter_no": data.meter_no}
        )

        return {
            "login": "success",
            "token": token
        }

    return {
        "login": "failed"
    }

@app.get("/monthly-revenue")
def monthly_revenue(
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT bill_date,
           SUM(bill_amount)
    FROM bills
    GROUP BY bill_date
    """)

    data = cursor.fetchall()

    conn.close()

    return data

@app.get("/revenue-chart")
def revenue_chart(
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT bill_date,
           SUM(bill_amount)
    FROM bills
    GROUP BY bill_date
    ORDER BY bill_date
    """)

    data = cursor.fetchall()

    conn.close()

    return data


@app.get("/consumer-history/{meter_no}")
def consumer_history(
    meter_no: str,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT bill_date,
                          units,
                          bill_amount,
                          payment_status
                   FROM bills
                   WHERE meter_no = %s
                   ORDER BY id DESC
                   """, (meter_no,))

    rows = cursor.fetchall()

    conn.close()


    return rows

@app.get("/consumer/{meter_no}")
def get_consumer(
    meter_no: str,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM consumer
    WHERE meter_no=%s
    """, (meter_no,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {
            "error": "Consumer Not Found"
        }

    return {
        "meter_no": row[0],
        "name": row[1],
        "mobile": row[2],
        "previous_reading": row[3]
    }

@app.get("/monthly-revenue")
def monthly_revenue(
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        bill_date,
        SUM(bill_amount)
    FROM bills
    WHERE payment_status='Paid'
    GROUP BY bill_date
    ORDER BY bill_date
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

@app.get("/latest-bill/{meter_no}")
def latest_bill(
    meter_no: str,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bill_date,
               units,
               bill_amount,
               payment_status
        FROM bills
        WHERE meter_no=%s
        ORDER BY id DESC
        LIMIT 1
    """, (meter_no,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {
            "error": "No Bill Found"
        }

    return {
        "bill_date": row[0],
        "units": row[1],
        "bill_amount": float(row[2]),
        "status": row[3]
    }

def generate_monthly_bills():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT meter_no,
               previous_reading
        FROM consumer
    """)

    consumers = cursor.fetchall()

    for meter_no, reading in consumers:

        units = 100

        bill_amount = units * 5

        cursor.execute("""
            INSERT INTO bills(
                meter_no,
                previous_reading,
                current_reading,
                units,
                bill_amount,
                bill_date,
                payment_status
            )
            VALUES(
                %s,%s,%s,%s,%s,
                CURRENT_DATE,
                'Pending'
            )
        """, (
            meter_no,
            reading,
            reading + units,
            units,
            bill_amount
        ))

    conn.commit()
    conn.close()

    print("Monthly Bills Generated")

@app.get("/analytics")
def analytics(token: str = Header(...)):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM consumer
    """)
    total_consumers = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bills
    """)
    total_bills = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bills
        WHERE payment_status='Paid'
    """)
    paid_bills = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bills
        WHERE payment_status='Pending'
    """)
    pending_bills = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(bill_amount),0)
        FROM bills
        WHERE payment_status='Paid'
    """)
    revenue = float(cursor.fetchone()[0])

    conn.close()

    return {
        "total_consumers": total_consumers,
        "total_bills": total_bills,
        "paid_bills": paid_bills,
        "pending_bills": pending_bills,
        "revenue": revenue
    }

@app.get("/predict/{meter_no}")
def predict_bill(
    meter_no: str,
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT current_reading
        FROM bills
        WHERE meter_no = %s
        ORDER BY id
    """, (meter_no,))

    rows = cursor.fetchall()

    readings = [row[0] for row in rows]

    if len(readings) < 3:
        return {
            "message": "Need at least 3 readings"
        }

    from ai_predictor import predict_next_reading

    prediction = predict_next_reading(readings)

    estimated_units = prediction - readings[-1]

    estimated_bill = estimated_units * 2.43

    return {
        "current_reading": readings[-1],
        "predicted_reading": prediction,
        "estimated_units": round(estimated_units, 2),
        "estimated_bill": round(estimated_bill, 2)
    }

@app.get("/theft-alerts")
def theft_alerts(
    token: str = Header(...)
):

    verify_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT meter_no,
               current_reading,
               theft_alert,
               bill_date
        FROM bills
        WHERE theft_alert='Theft Suspected'
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

@app.get("/usage-history/{meter_no}")
def usage_history(meter_no: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bill_date, units
        FROM bills
        WHERE meter_no=%s
        ORDER BY id
    """, (meter_no,))

    rows = cursor.fetchall()

    conn.close()

    return rows

@app.get("/init-db")
def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consumer(
        previous_reading INTEGER,
        meter_no VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100),
        mobile VARCHAR(20),
        email VARCHAR(100)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills(
        id SERIAL PRIMARY KEY,
        meter_no VARCHAR(20),
        bill_amount FLOAT,
        units INTEGER,
        status VARCHAR(20)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_history(
        id SERIAL PRIMARY KEY,
        meter_no VARCHAR(20),
        units INTEGER,
        reading_date TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_store(
        meter_no VARCHAR(20),
        otp VARCHAR(10),
        created_at TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    return {"status": "success"}
