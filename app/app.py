from pathlib import Path
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


#st.title("Jewelry Dashboard")
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
st.caption("Luxury Jewelry Price Visualization ✨")
           
engine = create_engine(
    "postgresql+psycopg2://sjchoi@localhost/jewelry"
)

df = pd.read_sql(
    "SELECT * FROM products",
    engine
)


df = pd.read_sql(
    "SELECT * FROM products",
    engine
)


# Product Search
# ==========================
st.subheader("🔍 Search")

keyword = st.text_input(
    "Enter product name"
)

if keyword:
    search_df = df[
        df["name"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]

    st.write(
        f"Search Result : {len(search_df)} items"
    )

    st.dataframe(search_df)
else:
    st.info(
        "product name please."
    )
# ==========================


st.metric("▸ Total Products", len(df))


# 컬렉션별 개수
st.subheader("💠 Products by Collection")

collection_count = df["collection"].value_counts()

st.bar_chart(collection_count)

st.info(
    f"» The {collection_count.idxmax()} collection "
    f"contains the most products."
)

# 가격 숫자 변환
df["price_num"] = (
    df["price"]
    .str.replace("₩", "")
    .str.replace(",", "")
    .str.strip()
)

df["price_num"] = pd.to_numeric(
    df["price_num"],
    errors="coerce"
)

df = df.dropna(subset=["price_num"])

df["price_num"] = df["price_num"].astype(int)


# 가격 통계1
st.subheader("💠 Price Statistics")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Price",
    f"₩ {df['price_num'].mean():,.0f}"
)

col2.metric(
    "Minimum Price",
    f"₩ {df['price_num'].min():,.0f}"
)

col3.metric(
    "Maximum Price",
    f"₩ {df['price_num'].max():,.0f}"
)

st.info(
    "» Compare average, minimum, and maximum prices across luxury jewelry products."
)


# 가격 통계2
st.subheader("💠 Collection Price Statistics")

stats_df = (
    df.groupby("collection")["price_num"]
    .agg(["mean", "min", "max"])
    .reset_index()
)

stats_df.columns = [
    "Collection",
    "Average Price",
    "Minimum Price",
    "Maximum Price"
]


# 원화 포맷
stats_df["Average Price"] = stats_df["Average Price"].apply(
    lambda x: f"₩ {x:,.0f}"
)

stats_df["Minimum Price"] = stats_df["Minimum Price"].apply(
    lambda x: f"₩ {x:,.0f}"
)

stats_df["Maximum Price"] = stats_df["Maximum Price"].apply(
    lambda x: f"₩ {x:,.0f}"
)

st.dataframe(stats_df)


# 가격 분포도
st.subheader("💠 Price Distribution")

max_price = df["price_num"].max()

bins = [
    0,
    1_000_000,
    3_000_000,
    5_000_000,
    10_000_000,
    20_000_000,
]

# 최고가가 2천만원보다 크면 마지막 bin 추가
if max_price > 20_000_000:
    bins.append(max_price)

labels = [
    "100만 원 이하",
    "100만 원 ~ 300만 원",
    "300만 원 ~ 500만 원",
    "500만 원 ~ 1,000만 원",
    "1,000만 원 ~ 2,000만 원",
]

# 마지막 구간 라벨 추가
if max_price > 20_000_000:
    labels.append("2,000만 원 이상")

df["price_range"] = pd.cut(
    df["price_num"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

price_dist = (
    df["price_range"]
    .value_counts()
    .sort_index()
)

st.bar_chart(price_dist)

dist_df = price_dist.reset_index()
dist_df.columns = ["Price Range", "Product Count"]

st.dataframe(dist_df)


# TOP 10 expensive jewelry
st.subheader("💠 Top 10 Most Expensive Jewelry")

top10 = df.sort_values(
    "price_num",
    ascending=False
).head(10)

st.dataframe(
    top10[["collection", "name", "price"]]
)


# 컬렉션 선택 필터
selected = st.selectbox(
    "▸ Select Collection",
    df["collection"].unique()
)

filtered = df[df["collection"] == selected]

st.subheader(f"💠 {selected} Products")
st.dataframe(filtered)


# 데이터 확인
st.subheader("📁 Raw Data")
with st.expander("View Raw Data"):
    st.dataframe(df)


#
st.markdown("---")
st.caption("Developed by @ssjjchoi")