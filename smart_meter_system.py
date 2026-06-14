import sqlite3
import random
import qrcode
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas


# ------------------------
# SMART METER FUNCTION
# ------------------------

def get_meter_reading(previous_reading):
    return previous_reading + random.randint(20, 100)


# ------------------------
# DATABASE CONNECTION
# ------------------------

conn = sqlite3.connect("electricity.db")
cursor = conn.cursor()

# ------------------------
# CREATE TABLES
# ------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS consumer(
    meter_no TEXT PRIMARY KEY,
    name TEXT,
    mobile TEXT,
    previous_reading INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meter_no TEXT,
    previous_reading INTEGER,
    current_reading INTEGER,
    units INTEGER,
    bill_amount REAL,
    bill_date TEXT,
    payment_status TEXT
)
""")

conn.commit()

# ------------------------
# ADD CONSUMERS
# ------------------------

consumers = [
    ('240069381738', 'K Vedavathi', '9391179191', 733),
    ('240069381739', 'Ramesh', '9876543210', 520),
    ('240069381740', 'Suresh', '9123456789', 610)
]

for consumer in consumers:
    try:
        cursor.execute(
            "INSERT INTO consumer VALUES (?, ?, ?, ?)",
            consumer
        )
    except:
        pass

conn.commit()

# ------------------------
# FETCH CONSUMERS
# ------------------------

cursor.execute("""
SELECT meter_no, name, mobile, previous_reading
FROM consumer
""")

all_consumers = cursor.fetchall()

# ------------------------
# BILL GENERATION
# ------------------------

for data in all_consumers:

    meter_no = data[0]
    name = data[1]
    mobile = data[2]
    previous_reading = data[3]

    current_reading = get_meter_reading(previous_reading)

    units = current_reading - previous_reading

    energy_charge = units * 2.25
    fixed_charge = 10
    customer_charge = 70
    electricity_duty = energy_charge * 0.025

    bill_amount = (
        energy_charge +
        fixed_charge +
        customer_charge +
        electricity_duty

    )
    # Due Date (15 days from bill generation)
    due_date = (
            datetime.now() +
            timedelta(days=15)
    ).strftime("%d-%m-%Y")

    # Late Fee
    late_fee = 50

    final_amount = bill_amount + late_fee

    # ------------------------
    # QR CODE GENERATION
    # ------------------------



    upi_link = (
        f"upi://pay?"
        f"pa=tsspdcl@upi"
        f"&pn=TSSPDCL"
        f"&am={round(bill_amount, 2)}"
    )

    img = qrcode.make(upi_link)

    img.save(f"{meter_no}_payment_qr.png")

    print("QR Code Generated:",
          f"{meter_no}_payment_qr.png")

    # EMAIL NOTIFICATION
    print("Email Notification Feature Disabled")

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
    VALUES(?,?,?,?,?,?,?)
    """, (
        meter_no,
        previous_reading,
        current_reading,
        units,
        round(bill_amount, 2),
        datetime.now().strftime("%d-%m-%Y"),
        "Pending"
    ))

    cursor.execute("""
    UPDATE consumer
    SET previous_reading = ?
    WHERE meter_no = ?
    """, (current_reading, meter_no))

    conn.commit()

    print("\n" + "=" * 50)
    print("DIGITAL ELECTRICITY BILL")
    print("=" * 50)

    print("Consumer :", name)
    print("Mobile   :", mobile)
    print("Meter No :", meter_no)

    print("Previous Reading :", previous_reading)
    print("Current Reading  :", current_reading)
    print("Units Consumed   :", units)

    print("Bill Amount      : ₹", round(bill_amount, 2))
    print("Due Date         :", due_date)
    print("Late Fee         : ₹", late_fee)
    print("Amount After Due : ₹", round(final_amount, 2))

    # ------------------------
    # PDF BILL GENERATION
    # ------------------------



    pdf_file = f"{meter_no}_bill.pdf"

    c = canvas.Canvas(pdf_file)

    c.drawString(100, 800, "DIGITAL ELECTRICITY BILL")
    c.drawString(100, 760, f"Consumer: {name}")
    c.drawString(100, 740, f"Meter No: {meter_no}")
    c.drawString(100, 720, f"Units Consumed: {units}")
    c.drawString(100, 700, f"Bill Amount: Rs.{round(bill_amount, 2)}")
    c.drawString(100, 680, f"Status: Pending")
    c.drawString(100, 680, f"Status: Pending")
    c.drawString(100, 660, f"Due Date: {due_date}")
    c.drawString(100, 640, f"Late Fee: Rs.{late_fee}")
    c.drawString(100, 620, f"Amount After Due: Rs.{round(final_amount, 2)}")



    due_date = (
            datetime.now() +
            timedelta(days=15)
    ).strftime("%d-%m-%Y")

    c.drawImage(
        f"{meter_no}_payment_qr.png",
        350,
        600,
        width=120,
        height=120
    )

    c.save()

    print(f"PDF Generated: {pdf_file}")


# ------------------------
# BILL HISTORY
# ------------------------

print("\n" + "=" * 50)
print("BILL HISTORY")
print("=" * 50)

cursor.execute("""
SELECT meter_no,
       units,
       bill_amount,
       bill_date,
       payment_status
FROM bills
ORDER BY id DESC
""")

rows = cursor.fetchall()

for row in rows:
    print(
        f"Meter: {row[0]} | "
        f"Units: {row[1]} | "
        f"Amount: ₹{row[2]} | "
        f"Date: {row[3]} | "
        f"Status: {row[4]}"
    )

conn.close()