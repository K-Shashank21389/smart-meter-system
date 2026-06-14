from reportlab.pdfgen import canvas

def generate_pdf(
        meter_no,
        name,
        units,
        bill_amount):

    pdf_file = f"{meter_no}_bill.pdf"

    c = canvas.Canvas(pdf_file)

    c.drawString(
        100,
        800,
        "DIGITAL ELECTRICITY BILL"
    )

    c.drawString(
        100,
        760,
        f"Consumer: {name}"
    )

    c.drawString(
        100,
        740,
        f"Meter No: {meter_no}"
    )

    c.drawString(
        100,
        720,
        f"Units Consumed: {units}"
    )

    c.drawString(
        100,
        700,
        f"Bill Amount: Rs.{bill_amount}"
    )

    c.save()

    return pdf_file