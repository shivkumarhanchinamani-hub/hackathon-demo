import streamlit as st
import pandas as pd

df = pd.read_csv("hackathon.csv")

st.set_page_config(layout="wide")
st.title("Revenue & Churn Early Warning Engine")

# ---------------- DERIVED LOGIC ----------------

def churn_risk(row):
    if row["Decline Yes / No"] == "YES" and row["Ticket Stress level"] == "High":
        return "High"
    elif row["Decline Yes / No"] == "YES":
        return "Medium"
    else:
        return "Low"

def usage_risk(row):
    if row["Decline Yes / No"] == "YES":
        return "High"
    elif row["Decline Yes / No"] == "Needs Review":
        return "Review"
    else:
        return "Low"

def growth_opportunity(row):
    if row["Decline Yes / No"] == "NO" and row["ARR"] > 50000:
        return "High"
    elif row["Decline Yes / No"] == "NO":
        return "Medium"
    else:
        return "Low"

df["Churn Risk"] = df.apply(churn_risk, axis=1)
df["Usage Risk"] = df.apply(usage_risk, axis=1)
df["Growth Opportunity"] = df.apply(growth_opportunity, axis=1)

df["Revenue at Risk"] = df.apply(
    lambda row: row["ARR"] * 0.6 if row["Churn Risk"] == "High"
    else row["ARR"] * 0.3 if row["Churn Risk"] == "Medium"
    else row["ARR"] * 0.1,
    axis=1
)

# ---------------- KPI SECTION ----------------

total_arr = df["ARR"].sum()
revenue_risk = df["Revenue at Risk"].sum()
high_churn = (df["Churn Risk"] == "High").sum()
growth_accounts = (df["Growth Opportunity"] == "High").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Portfolio ARR", f"${total_arr:,.0f}")
col2.metric("Revenue at Risk", f"${revenue_risk:,.0f}")
col3.metric("High Churn Risk", high_churn)
col4.metric("Growth Opportunities", growth_accounts)

st.divider()

# ---------------- FILTERS ----------------

st.sidebar.header("Filters")

churn_filter = st.sidebar.multiselect(
    "Churn Risk",
    df["Churn Risk"].unique(),
    default=df["Churn Risk"].unique()
)

growth_filter = st.sidebar.multiselect(
    "Growth Opportunity",
    df["Growth Opportunity"].unique(),
    default=df["Growth Opportunity"].unique()
)

usage_filter = st.sidebar.multiselect(
    "Usage Risk",
    df["Usage Risk"].unique(),
    default=df["Usage Risk"].unique()
)

filtered_df = df[
    (df["Churn Risk"].isin(churn_filter)) &
    (df["Growth Opportunity"].isin(growth_filter)) &
    (df["Usage Risk"].isin(usage_filter))
]

# ---------------- TABLE VIEW ----------------

st.subheader("Portfolio Intelligence View")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ---------------- ACCOUNT INTELLIGENCE ----------------

st.subheader("Account Intelligence")

account = st.selectbox("Select Account", filtered_df["Accounts"])

acc_data = df[df["Accounts"] == account].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("ARR", f"${acc_data['ARR']:,.0f}")
col2.metric("Churn Risk", acc_data["Churn Risk"])
col3.metric("Usage Risk", acc_data["Usage Risk"])
col4.metric("Growth Opportunity", acc_data["Growth Opportunity"])

st.write("### Revenue Impact")

st.metric("Revenue at Risk", f"${acc_data['Revenue at Risk']:,.0f}")

st.write("### Recommended Action")

if acc_data["Churn Risk"] == "High":
    st.error("🔥 Exec Alignment + Recovery Plan")

elif acc_data["Usage Risk"] == "High":
    st.warning("Usage Recovery Intervention")

elif acc_data["Ticket Stress level"] == "High":
    st.warning("Technical Health Review")

elif acc_data["Growth Opportunity"] == "High":
    st.success("🚀 Expansion / Upsell Play")

else:
    st.info("Monitor")
