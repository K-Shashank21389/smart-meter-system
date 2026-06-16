from db import get_connection

conn = get_connection()
cur = conn.cursor()

for i in range(1, 6):

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
        %s,%s,%s,%s,%s,
        CURRENT_DATE - (%s * INTERVAL '30 days'),
        %s,%s
    )
    """,
    (
        "240069381738",
        1000 + (i * 100),
        1100 + (i * 100),
        100 + (i * 10),
        500 + (i * 50),
        i,
        "Paid",
        "Normal"
    ))

conn.commit()
conn.close()

print("History added")