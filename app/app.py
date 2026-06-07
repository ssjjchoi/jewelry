from pathlib import Path
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import os

st.markdown(
    """
    <h1 style='
        color:#0F8F6F;
        font-size:45px;
        text-align:center;
    '>
        💎 Jewelry Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

st.caption("Luxury Jewelry Price Visualization")


DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://sjchoi@localhost/jewelry")

engine = create_engine(DB_URL)


# DATA LOAD (CACHE)
@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM products", engine)


# PREPROCESS
def preprocess(df):
    df = df.copy()

    df["price_num"] = (
        df["price"]
        .str.replace(r"[^\d]", "", regex=True)
    )

    df["price_num"] = pd.to_numeric(df["price_num"], errors="coerce")
    df = df.dropna(subset=["price_num"])
    df["price_num"] = df["price_num"].astype(int)

    return df

df = load_data()
df = preprocess(df)


# SEARCH
keyword = st.text_input("🔍 Enter product name")

if keyword:
    search_df = df[
        df["name"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]

    st.write(f"Search Result : {len(search_df)} items")
    st.dataframe(search_df)


# BASIC METRIC
st.metric("▸ Total Products", len(df))


# COLLECTION COUNT
st.subheader("💠 Products by Collection")

collection_count = df["collection"].value_counts()

st.bar_chart(collection_count)

if not collection_count.empty:
    st.info(f"» The {collection_count.idxmax()} collection contains the most products.")


# PRICE STATS
st.subheader("💠 Price Statistics")

if len(df) > 0:
    col1, col2, col3 = st.columns(3)

    col1.metric("Average Price", f"₩ {df['price_num'].mean():,.0f}")
    col2.metric("Minimum Price", f"₩ {df['price_num'].min():,.0f}")
    col3.metric("Maximum Price", f"₩ {df['price_num'].max():,.0f}")

    st.info("» Compare average, minimum, and maximum prices across products.")


# GROUP STATS
st.subheader("💠 Collection Price Statistics")

stats_df = (
    df.groupby("collection")["price_num"]
    .agg(["mean", "min", "max"])
    .reset_index()
)

stats_df.columns = ["Collection", "Average Price", "Minimum Price", "Maximum Price"]

for col in ["Average Price", "Minimum Price", "Maximum Price"]:
    stats_df[col] = stats_df[col].apply(lambda x: f"₩ {x:,.0f}")

st.dataframe(stats_df)


# DISTRIBUTION
st.subheader("💠 Price Distribution")

if len(df) > 0:
    max_price = df["price_num"].max()

    bins = [0, 1_000_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000]

    if max_price > 20_000_000:
        bins.append(max_price)

    labels = [
        "100만 원 이하",
        "100만 원 ~ 300만 원",
        "300만 원 ~ 500만 원",
        "500만 원 ~ 1,000만 원",
        "1,000만 원 ~ 2,000만 원",
    ]

    if max_price > 20_000_000:
        labels.append("2,000만 원 이상")

    df["price_range"] = pd.cut(df["price_num"], bins=bins, labels=labels, include_lowest=True)

    price_dist = df["price_range"].value_counts().sort_index()

    st.bar_chart(price_dist)

    dist_df = price_dist.reset_index()
    dist_df.columns = ["Price Range", "Product Count"]

    st.dataframe(dist_df)


# TOP 10
st.subheader("💠 Top 10 Most Expensive Jewelry")

top10 = df.sort_values("price_num", ascending=False).head(10)

st.dataframe(top10[["collection", "name", "price"]])


# FILTER
st.subheader("🔎 Filter Products")

selected = st.selectbox("▸ Select Collection", df["collection"].dropna().unique())

filtered = df[df["collection"] == selected]

if len(filtered) > 0:
    min_price = int(filtered["price_num"].min())
    max_price = int(filtered["price_num"].max())

    price_range = st.slider(
        "💰 Select Price Range",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )

    filtered = filtered[
        (filtered["price_num"] >= price_range[0]) &
        (filtered["price_num"] <= price_range[1])
    ]

    st.write(f"Showing {len(filtered)} products")
    st.dataframe(filtered)


# RAW DATA
st.subheader("📁 Raw Data")

with st.expander("View Raw Data"):
    st.dataframe(df)

st.markdown("---")
st.caption("Developed by @ssjjchoi")