import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Smart Meter Admin",
    layout="wide"
)

st.title("⚡ Smart Meter Admin Dashboard")

token = st.text_input(
    "JWT Token",
    type="password"
)

if token:

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Dashboard",
            "Consumers",
            "Bills",
            "Analytics",
            "Search Consumer",
            "Theft Alerts"
        ]
    )

    # DASHBOARD
    if menu == "Dashboard":

        response = requests.get(
            "http://127.0.0.1:8000/dashboard",
            headers={"token": token}
        )



        if response.status_code == 200:

            data = response.json()

            

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Consumers", data["total_consumers"])
            col2.metric("Bills", data["total_bills"])
            col3.metric("Paid", data["paid_bills"])
            col4.metric("Pending", data["pending_bills"])
            col5.metric("Revenue ₹", data["revenue"])

        else:
            st.error(response.text)

    # CONSUMERS
    elif menu == "Consumers":

        response = requests.get(
            "http://127.0.0.1:8000/consumers",
            headers={"token": token}
        )

        if response.status_code == 200:

            df = pd.DataFrame(
                response.json(),
                columns=[
                    "Meter No",
                    "Name",
                    "Mobile",
                    "Previous Reading"
                ]
            )

            st.dataframe(
                df,
                width="stretch"
            )


    # BILLS
    elif menu == "Bills":

        response = requests.get(
            "http://127.0.0.1:8000/bills",
            headers={"token": token}
        )

        if response.status_code == 200:

            df = pd.DataFrame(
                response.json()
            )

            st.dataframe(
                df,
                width="stretch"
            )

        else:
            st.error(response.text)


    # ANALYTICS
    elif menu == "Analytics":

        response = requests.get(
            "http://127.0.0.1:8000/monthly-revenue",
            headers={"token": token}
        )

        if response.status_code == 200:

            data = response.json()

            df = pd.DataFrame(
                data,
                columns=[
                    "Date",
                    "Revenue"
                ]
            )

            st.subheader("Revenue Trend")

            st.dataframe(df)

            fig = px.bar(
                df,
                x="Date",
                y="Revenue",
                title="Revenue Collection"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:
            st.error(response.text)


    elif menu == "Search Consumer":

        meter_no = st.text_input(
            "Enter Meter Number"
        )

        if st.button("Search"):

            response = requests.get(
                f"http://127.0.0.1:8000/consumer/{meter_no}",
                headers={"token": token}
            )

            if response.status_code == 200:

                data = response.json()



                fig = px.pie(
                    # chart_df,
                    names="Category",
                    values="Count",
                    title="Bill Payment Status"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                if "error" in data:
                    st.error(data["error"])

                else:

                    st.success("Consumer Found")

                    st.write(
                        "Meter No:",
                        data["meter_no"]
                    )

                    st.write(
                        "Name:",
                        data["name"]
                    )

                    st.write(
                        "Mobile:",
                        data["mobile"]
                    )

                    st.write(
                        "Previous Reading:",
                        data["previous_reading"]
                    )

                    history = requests.get(
                        f"http://127.0.0.1:8000/consumer-history/{meter_no}",
                        headers={"token": token}
                    )

                    if history.status_code == 200:
                        history_df = pd.DataFrame(
                            history.json(),
                            columns=[
                                "Bill Date",
                                "Units",
                                "Amount",
                                "Status"
                            ]
                        )

                        st.subheader("Bill History")

                        st.dataframe(history_df)

    elif menu == "Theft Alerts":

        response = requests.get(
            "http://127.0.0.1:8000/theft-alerts",
            headers={
                "token": token
            }
        )

        if response.status_code == 200:
            import pandas as pd

            df = pd.DataFrame(
                response.json(),
                columns=[
                    "Meter Number",
                    "Current Reading",
                    "Alert",
                    "Date"
                ]
            )

            st.error("⚠ Theft Detection Alerts")

            st.dataframe(
                df,
                use_container_width=True
            )