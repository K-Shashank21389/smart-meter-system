import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("electricity.db")
cursor = conn.cursor()

cursor.execute("""
SELECT meter_no, bill_amount
FROM bills
ORDER BY id DESC
LIMIT 10
""")

rows = cursor.fetchall()

meters = []
amounts = []


for row in rows:
    meters.append(row[0])
    amounts.append(row[1])

plt.figure(figsize=(8, 5))
plt.bar(meters, amounts)

plt.title("Electricity Bill Revenue")
plt.xlabel("Meter Number")
plt.ylabel("Bill Amount")



plt.show()

conn.close()