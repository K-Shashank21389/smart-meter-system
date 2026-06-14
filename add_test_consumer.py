from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT INTO consumer
(meter_no, name, mobile, email, previous_reading)
VALUES
(
    '240069381738',
    'Shashank',
    '+91XXXXXXXXXX',
    'yourmail@gmail.com',
    0
)
ON CONFLICT (meter_no)
DO NOTHING
""")

conn.commit()
conn.close()

print("Consumer added")