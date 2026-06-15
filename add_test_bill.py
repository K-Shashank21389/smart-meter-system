from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
INSERT INTO bills(
    meter_no,
    previous_reading,
    current_reading,
    units,
    bill_amount,
    bill_date,
    payment_status,
    theft_alert
)
VALUES(
    %s,%s,%s,%s,%s,CURRENT_DATE,%s,%s
)
""",
(
    "240069381738",
    1000,
    1100,
    100,
    500,
    "Pending",
    "Normal"
))

conn.commit()
conn.close()

print("Bill inserted")