import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="NEPSE Floorsheet", layout="wide")

st.title("NEPSE Floorsheet")

API_URL = "https://nepselytics-6d61dea19f30.herokuapp.com/api/nepselytics/floorsheet"

# Sidebar
st.sidebar.header("Controls")
page = st.sidebar.number_input("Page", min_value=1, value=1)
size = st.sidebar.selectbox("Page Size", [10, 20, 100])
order = st.sidebar.selectbox("Order", ["desc", "asc"])

@st.cache_data(ttl=10)
def fetch_data(page, size, order):
    params = {
        "page": page,
        "Size": size,
        "order": order
    }
    res = requests.get(API_URL, params=params, timeout=10)
    res.raise_for_status()
    return res.json()

try:
    result = fetch_data(page, size, order)
    data = result["data"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Trades", f"{data['totalTrades']:,}")
    c2.metric("Total Quantity", f"{data['totalQty']:,}")
    c3.metric("Total Amount", f"{data['totalAmount']:,.2f}")

    rows = []
    for r in data["content"]:
        rows.append({
            "CONTRACT": r["contractId"],
            "SYMBOL": r["symbol"],
            "BUYER": r["buyerMemberId"],
            "SELLER": r["sellerMemberId"],
            "QTY": r["contractQuantity"],
            "PRICE": r["contractRate"],
            "AMOUNT": r["contractAmount"],
            "TIME": datetime.fromisoformat(
                r["tradeTime"].replace("Z", "")
            ).strftime("%H:%M:%S")
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=500)

    st.caption(
        f"Page {data['pageIndex']} of {data['totalPages']} | "
        f"Total Records: {data['totalItems']:,}"
    )

except Exception as e:
    st.error("Failed to load data")
    st.exception(e)
