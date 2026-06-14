import qrcode

def generate_qr(
        meter_no,
        bill_amount):

    upi_link = (
        f"upi://pay?"
        f"pa=tsspdcl@upi"
        f"&pn=TSSPDCL"
        f"&am={bill_amount}"
    )

    img = qrcode.make(
        upi_link
    )

    qr_file = (
        f"{meter_no}_payment_qr.png"
    )

    img.save(qr_file)

    return qr_file