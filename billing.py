def calculate_bill(previous_reading, current_reading):

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

    return {
        "units": units,
        "energy_charge": round(energy_charge, 2),
        "fixed_charge": fixed_charge,
        "customer_charge": customer_charge,
        "electricity_duty": round(electricity_duty, 2),
        "bill_amount": round(bill_amount, 2)
    }