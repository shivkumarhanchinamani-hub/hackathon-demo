import streamlit as st
import pandas as pd

df = pd.read_csv("hackathon.csv")

st.set_page_config(layout="wide")
st.title("Revenue & Churn Early Warning Engine")

total_arr = df["ARR"].sum()
high_stress = (df["Ticket Stress level"] == "High").sum()
renewals = (df["Renewal"] == "YES").sum()
decline_accounts = (df["Decline Yes / No"] == "YES").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Portfolio ARR", f"${total_arr:,.0f}")
col2.metric("Declining Accounts", decline_accounts)
col3.metric("High Stress Accounts", high_stress)
col4.metric("Upcoming Renewals", renewals)

st.divider()

st.subheader("Portfolio Risk View")
st.dataframe(df, use_container_width=True)

st.divider()

st.subheader("Account Intelligence")

account = st.selectbox("Select Account", df["Accounts"])
acc_data = df[df["Accounts"] == account].iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric("ARR", f"${acc_data['ARR']:,.0f}")
col2.metric("Ticket Stress", acc_data["Ticket Stress level"])
col3.metric("Renewal", acc_data["Renewal"])

st.write("### Recommended Action")

if acc_data["Decline Yes / No"] == "Needs Review":
    st.warning("Data Validation Required")

elif acc_data["Decline Yes / No"] == "YES" and acc_data["Ticket Stress level"] == "High":
    st.error("🔥 Exec Alignment + Recovery Plan")

elif acc_data["Decline Yes / No"] == "YES":
    st.warning("Usage Recovery Intervention")

elif acc_data["Ticket Stress level"] == "High":
    st.warning("Technical Health Review")

elif acc_data["ARR"] > 50000:
    st.success("Expansion / Upsell Play")

else:
    st.info("Monitor")
