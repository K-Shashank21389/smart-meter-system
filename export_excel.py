import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("electricity.db")

# Read bills table
query = """
SELECT meter_no,
       previous_reading,
       current_reading,
       units,
       bill_amount,
       bill_date,
       payment_status
FROM bills
"""

df = pd.read_sql_query(query, conn)

# Export to Excel
df.to_excel(
    "electricity_bills.xlsx",
    index=False
)

conn.close()

print("Excel file created successfully!")