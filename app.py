import streamlit as st
import pandas as pd

df = pd.read_csv("hackathon.csv")

st.set_page_config(layout="wide")
st.title("Revenue & Churn Early Warning Engine")

# ---------------- CATEGORY LOGIC ----------------

def classify_account(row):

    # 1️⃣ CHURN RISK (Highest Priority)
    if row["Decline Yes / No"] == "YES" and row["Ticket Stress level"] == "High":
        return "Churn Risk 🔴"

    # 2️⃣ RENEWAL RISK
    elif row["Renewal"] == "YES":
        return "Renewal Risk ⏳"

    # 3️⃣ USAGE DECLINE
    elif row["Decline Yes / No"] == "YES":
        return "Usage Decline 📉"

    # 4️⃣ NEEDS EXTRA CARE (Support Stress)
    elif row["Ticket Stress level"] == "High":
        return "Needs Extra Care 🔧"

    # 5️⃣ GROWTH OPPORTUNITY
    elif row["Decline Yes / No"] == "NO" and row["ARR"] > 50000:
        return "Growth Opportunity 🚀"

    # 6️⃣ LOW ENGAGEMENT RISK
    elif row["Decline Yes / No"] == "NO" and row["Usage Jan"] <= 2.5:
        return "Low Engagement Risk 🟡"

    # 7️⃣ STABLE ACCOUNTS (Default)
    else:
        return "Stable Accounts ✅"


df["Portfolio Category"] = df.apply(classify_account, axis=1)

# ---------------- REVENUE AT RISK ----------------

df["Revenue at Risk"] = df.apply(
    lambda row: row["ARR"] * 0.6 if "Churn Risk" in row["Portfolio Category"]
    else row["ARR"] * 0.3 if "Usage Decline" in row["Portfolio Category"]
    else row["ARR"] * 0.2 if "Renewal Risk" in row["Portfolio Category"]
    else row["ARR"] * 0.1,
    axis=1
)

# ---------------- KPI SECTION ----------------

total_arr = df["ARR"].sum()
revenue_risk = df["Revenue at Risk"].sum()
churn_accounts = (df["Portfolio Category"] == "Churn Risk 🔴").sum()
growth_accounts = (df["Portfolio Category"] == "Growth Opportunity 🚀").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Portfolio ARR", f"${total_arr:,.0f}")
col2.metric("Revenue at Risk", f"${revenue_risk:,.0f}")
col3.metric("Churn Risk Accounts", churn_accounts)
col4.metric("Growth Opportunities", growth_accounts)

st.divider()

# ---------------- SINGLE INTELLIGENCE FILTER ----------------

category = st.sidebar.selectbox(
    "Portfolio Intelligence Lens",
    ["All"] + list(df["Portfolio Category"].unique())
)

if category == "All":
    filtered_df = df
else:
    filtered_df = df[df["Portfolio Category"] == category]

# ---------------- TABLE VIEW ----------------

st.subheader("Portfolio Intelligence View")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ---------------- ACCOUNT INTELLIGENCE ----------------

if len(filtered_df) > 0:

    account = st.selectbox("Select Account", filtered_df["Accounts"])
    acc_data = df[df["Accounts"] == account].iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("ARR", f"${acc_data['ARR']:,.0f}")
    col2.metric("Category", acc_data["Portfolio Category"])
    col3.metric("Revenue at Risk", f"${acc_data['Revenue at Risk']:,.0f}")

    st.write("### Recommended Action")

    if "Churn Risk" in acc_data["Portfolio Category"]:
        st.error("🔥 Exec Alignment + Recovery Plan")

    elif "Usage Decline" in acc_data["Portfolio Category"]:
        st.warning("Usage Recovery Intervention")

    elif "Needs Extra Care" in acc_data["Portfolio Category"]:
        st.warning("Technical / Support Stabilization")

    elif "Renewal Risk" in acc_data["Portfolio Category"]:
        st.warning("Renewal Engagement Strategy")

    elif "Growth Opportunity" in acc_data["Portfolio Category"]:
        st.success("🚀 Expansion / Upsell Play")

    elif "Low Engagement Risk" in acc_data["Portfolio Category"]:
        st.warning("Proactive Engagement Recommended")

    else:
        st.info("Monitor")

else:
    st.warning("No accounts match selected category")
