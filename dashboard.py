import os
import sqlite3
import sys
from PyQt5.QtWidgets import *


# ------------------------
# FUNCTIONS
# ------------------------

def show_consumers():

    conn = sqlite3.connect("electricity.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM consumer")

    rows = cursor.fetchall()

    msg = ""

    for row in rows:
        msg += str(row) + "\n"

    QMessageBox.information(
        window,
        "Consumers",
        msg
    )

    conn.close()

def show_history():

    conn = sqlite3.connect("electricity.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT meter_no,
       units,
       bill_amount,
       bill_date,
       payment_status
FROM bills
    """)

    f"Status: {row[4]}\n"
    rows = cursor.fetchall()

    msg = ""

    for row in rows:
        msg += (
            f"Meter: {row[0]}\n"
            f"Units: {row[1]}\n"
            f"Amount: ₹{row[2]}\n"
            f"Date: {row[3]}\n"
            "----------------------\n"
        )

    if not msg:
        msg = "No Bills Found"

    QMessageBox.information(
        window,
        "Bill History",
        msg
    )

    conn.close()

def generate_bills():

    os.system("python smart_meter_system.py")

    load_stats()

    QMessageBox.information(
        window,
        "Success",
        "Bills Generated Successfully"
    )

def show_history_table():

    conn = sqlite3.connect("electricity.db")
    cursor = conn.cursor()

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

    table_window = QWidget()
    table_window.setWindowTitle("Bill History")
    table_window.resize(800, 400)

    layout = QVBoxLayout()

    table = QTableWidget()

    table.setRowCount(len(rows))
    table.setColumnCount(5)

    table.setHorizontalHeaderLabels([
        "Meter No",
        "Units",
        "Amount",
        "Date",
        "Status"
    ])

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            table.setItem(
                i,
                j,
                QTableWidgetItem(str(value))
            )

    layout.addWidget(table)

    table_window.setLayout(layout)

    table_window.show()

    global history_window
    history_window = table_window

    conn.close()



def load_stats():

    conn = sqlite3.connect("electricity.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM consumer")
    consumers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bills")
    bills = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(bill_amount) FROM bills")
    revenue = cursor.fetchone()[0]

    if revenue is None:
        revenue = 0

    total_consumers_label.setText(
        f"Total Consumers: {consumers}"
    )

    total_bills_label.setText(
        f"Total Bills: {bills}"
    )

    total_revenue_label.setText(
        f"Total Revenue: ₹{round(revenue,2)}"
    )

    conn.close()

def mark_paid():

    conn = sqlite3.connect("electricity.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE bills
    SET payment_status='Paid'
    WHERE id = (
        SELECT MAX(id)
        FROM bills
    )
    """)

    conn.commit()
    conn.close()

    QMessageBox.information(
        window,
        "Payment",
        "Latest Bill Marked as Paid"
    )
def search_consumer():

    meter_no = meter_input.text()

    conn = sqlite3.connect("electricity.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM consumer
    WHERE meter_no=?
    """, (meter_no,))

    row = cursor.fetchone()

    conn.close()

    if row:

        msg = (
            f"Meter No: {row[0]}\n"
            f"Name: {row[1]}\n"
            f"Mobile: {row[2]}\n"
            f"Current Reading: {row[3]}"
        )

        QMessageBox.information(
            window,
            "Consumer Details",
            msg
        )

    else:

        QMessageBox.warning(
            window,
            "Not Found",
            "Consumer Not Found"
        )
def export_excel():

    import pandas as pd

    conn = sqlite3.connect("electricity.db")

    query = """
    SELECT *
    FROM bills
    """

    df = pd.read_sql_query(query, conn)

    df.to_excel(
        "electricity_bills.xlsx",
        index=False
    )

    conn.close()

    QMessageBox.information(
        window,
        "Export Complete",
        "electricity_bills.xlsx created successfully"
    )

def show_bill_table():

    conn = sqlite3.connect("electricity.db")
    cursor = conn.cursor()

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

    table_window = QWidget()
    table_window.setWindowTitle("Bill History")
    table_window.resize(800, 500)

    layout = QVBoxLayout()

    table = QTableWidget()

    table.setRowCount(len(rows))
    table.setColumnCount(5)

    table.setHorizontalHeaderLabels([
        "Meter No",
        "Units",
        "Bill Amount",
        "Bill Date",
        "Status"
    ])

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            table.setItem(
                i,
                j,
                QTableWidgetItem(str(value))
            )

    table.resizeColumnsToContents()

    layout.addWidget(table)

    table_window.setLayout(layout)
    table_window.show()

    global bill_window
    bill_window = table_window

    conn.close()


# ------------------------
# GUI
# ------------------------

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Smart Electricity Billing System")
window.resize(600, 400)

layout = QVBoxLayout()

title = QLabel("SMART ELECTRICITY BILLING SYSTEM")
layout.addWidget(title)

btn1 = QPushButton("Generate Bills")
btn1.clicked.connect(generate_bills)
layout.addWidget(btn1)

btn2 = QPushButton("View Consumers")
btn2.clicked.connect(show_consumers)
layout.addWidget(btn2)

btn3 = QPushButton("View Bill History")
btn3.clicked.connect(show_bill_table)
layout.addWidget(btn3)

btn4 = QPushButton("Exit")
btn4.clicked.connect(window.close)
layout.addWidget(btn4)

btn5 = QPushButton("Mark Latest Bill as Paid")
layout.addWidget(btn5)
btn5.clicked.connect(mark_paid)

total_consumers_label = QLabel()
layout.addWidget(total_consumers_label)

total_bills_label = QLabel()
layout.addWidget(total_bills_label)

total_revenue_label = QLabel()
layout.addWidget(total_revenue_label)

search_label = QLabel("Enter Meter Number")
layout.addWidget(search_label)

meter_input = QLineEdit()
layout.addWidget(meter_input)

search_btn = QPushButton("Search Consumer")
layout.addWidget(search_btn)
search_btn.clicked.connect(search_consumer)

btn_export = QPushButton("Export Bills To Excel")
btn_export.clicked.connect(export_excel)
layout.addWidget(btn_export)

window.setLayout(layout)

load_stats()

window.show()

sys.exit(app.exec_())