import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="NEPSE Floorsheet", layout="wide")

st.title("📊 NEPSE Floorsheet (Live)")

# Sidebar controls
st.sidebar.header("Controls")
page = st.sidebar.number_input("Page", min_value=1, value=1)
size = st.sidebar.selectbox("Page Size", [10, 20, 50, 100])
order = st.sidebar.selectbox("Order", ["desc", "asc"])

API_URL = "https://nepselytics-6d61dea19f30.herokuapp.com/api/nepselytics/floorsheet"

params = {
    "page": page,
    "Size": size,
    "order": order
}

@st.cache_data(ttl=10)
def fetch_data(params):
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

try:
    result = fetch_data(params)
    data = result["data"]

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", f"{data['totalTrades']:,}")
    col2.metric("Total Quantity", f"{data['totalQty']:,}")
    col3.metric("Total Amount", f"{data['totalAmount']:,.2f}")

    rows = []
    for r in data["content"]:
        rows.append({
            "CONTRACT": r["contractId"],
            "SYMBOL": r["symbol"],
            "BUYER": r["buyerBrokerName"],
            "SELLER": r["sellerBrokerName"],
            "QTY": r["contractQuantity"],
            "PRICE": r["contractRate"],
            "AMOUNT": r["contractAmount"],
            "TIME": datetime.fromisoformat(
                r["tradeTime"].replace("Z", "")
            ).strftime("%H:%M:%S")
        })

    df = pd.DataFrame(rows)

    st.subheader("Floorsheet Data")
    st.dataframe(df, use_container_width=True, height=500)

    # Pagination info
    st.caption(
        f"Page {data['pageIndex']} of {data['totalPages']} | "
        f"Total Records: {data['totalItems']:,}"
    )

except Exception as e:
    st.error("Failed to fetch data")
    st.exception(e)
