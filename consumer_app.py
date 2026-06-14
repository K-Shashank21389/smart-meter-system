import streamlit as st
import requests

import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Consumer Portal"
)

st.title("⚡ Consumer Portal")

meter_no = st.text_input(
    "Meter Number"
)

if "token" not in st.session_state:
    st.session_state.token = None

if st.button("Send OTP"):

    response = requests.post(
        "http://127.0.0.1:8000/send-otp",
        json={
            "meter_no": meter_no
        }
    )

    st.success("OTP Sent")

otp = st.text_input(
    "Enter OTP"
)

if st.button("Verify OTP"):

    response = requests.post(
        "http://127.0.0.1:8000/verify-otp",
        json={
            "meter_no": meter_no,
            "otp": otp
        }
    )



    data = response.json()

    if data.get("login") == "success":

        st.session_state.token = data["token"]

        st.success("Login Successful")

    else:

        st.error("Invalid OTP")

if st.session_state.token:

    st.subheader("Bill History")

    response = requests.get(
        f"http://127.0.0.1:8000/consumer-bills/{meter_no}",
        headers={
            "token": st.session_state.token
        }
    )

    latest = requests.get(
        f"http://127.0.0.1:8000/latest-bill/{meter_no}",
        headers={
            "token": st.session_state.token
        }
    )

    bill = latest.json()

    st.subheader("Current Bill")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Units",
        bill["units"]
    )

    col2.metric(
        "Amount ₹",
        bill["bill_amount"]
    )

    col3.metric(
        "Status",
        bill["status"]
    )

    import pandas as pd

    df = pd.DataFrame(
        response.json(),
        columns=[
            "Bill Date",
            "Units",
            "Bill Amount",
            "Status"
        ]
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader("Pay Latest Bill")

    if st.button("Pay Bill"):
        response = requests.post(
            "http://127.0.0.1:8000/pay-bill",
            json={
                "meter_no": meter_no
            },
            headers={
                "token": st.session_state.token
            }
        )

        st.success(response.json()["status"])

    st.subheader("Download Bill")

    if st.button("Get PDF"):

        st.write("Meter Number:", meter_no)

        response = requests.get(
            f"http://127.0.0.1:8000/bill/{meter_no}",
            headers={
                "token": st.session_state.token
            }
        )

        if response.status_code == 200:

            st.download_button(
                label="Download PDF Bill",
                data=response.content,
                file_name=f"{meter_no}_bill.pdf",
                mime="application/pdf"
            )

        else:

            st.error(f"Status Code: {response.status_code}")
            st.write(response.text)

    history = requests.get(
        f"http://127.0.0.1:8000/usage-history/{meter_no}",
        headers={
            "token": st.session_state.token
        }
    )

    if history.status_code == 200:
        df = pd.DataFrame(
            history.json(),
            columns=[
                "Date",
                "Units"
            ]
        )

        fig = px.line(
            df,
            x="Date",
            y="Units",
            title="Electricity Usage Trend",
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )