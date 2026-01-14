import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from time import sleep

st.set_page_config(page_title="NEPSE Floorsheet (All)", layout="wide")
st.title("NEPSE Floorsheet (All Records)")

API_URL = "https://nepselytics-6d61dea19f30.herokuapp.com/api/nepselytics/floorsheet"

# Sidebar
st.sidebar.header("Controls")
order = st.sidebar.selectbox("Order", ["desc", "asc"])
st.sidebar.markdown(
    "⚠️ Fetching all records may take a while depending on total trades."
)

@st.cache_data(ttl=600)
def fetch_all_data(order="desc"):
    all_rows = []
    page = 1
    page_size = 100  # fetch 100 rows per request to reduce API calls

    while True:
        params = {
            "page": page,
            "Size": page_size,
            "order": order
        }

        res = requests.get(API_URL, params=params, timeout=10)
        res.raise_for_status()
        result = res.json()["data"]

        # Add rows from this page
        all_rows.extend(result["content"])

        # Check if more pages
        if result["hasNext"]:
            page += 1
            sleep(0.1)  # small delay to avoid hammering the API
        else:
            break

    return all_rows

try:
    with st.spinner("Fetching all floorsheet records..."):
        rows = fetch_all_data(order)

    # Convert to DataFrame
    df_rows = []
    for r in rows:
        df_rows.append({
            "CONTRACT": r["contractId"],
            "SYMBOL": r["symbol"],
            "BUYER": r["buyerMemberId"],
            "SELLER": r["sellerMemberId"],
            "QTY": r["contractQuantity"],
            "PRICE": r["contractRate"],
            "AMOUNT": r["contractAmount"],
            "TIME": datetime.fromisoformat(r["tradeTime"].replace("Z", "")).strftime("%H:%M:%S")
        })

    df = pd.DataFrame(df_rows)

    st.success(f"Fetched {len(df)} records!")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Failed to load data")
    st.exception(e)
