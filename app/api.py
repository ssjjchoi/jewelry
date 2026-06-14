from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine
import os

class SearchResponse(BaseModel):
    count: int
    items: list

app = FastAPI()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://localhost/jewelry"
)

engine = create_engine(DATABASE_URL)

@app.get("/")
def root():
    return {
        "message": "Jewelry API",
        "endpoints": [
            "/search",
            "/collections",
            "/stats"
        ]
    }

@app.get("/search", response_model=SearchResponse)
def search(
    keyword: str = "",
    min_price: int = 0,
    max_price: int = 999999999,
    sort: str = "price_asc",
    limit: int = Query(
    default=20,
    ge=1,
    le=100
    ),

    offset: int = Query(
        default=0,
        ge=0
    )
):

    SORT_OPTIONS = {
        "price_asc": "price ASC",
        "price_desc": "price DESC"
    }

    order_by = SORT_OPTIONS.get(sort, "price ASC")

    query = f"""
    SELECT *
    FROM products
    WHERE name ILIKE %(keyword)s
      AND price >= %(min_price)s
      AND price <= %(max_price)s
    ORDER BY {order_by}
    LIMIT %(limit)s
    OFFSET %(offset)s
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "keyword": f"%{keyword}%",
            "min_price": min_price,
            "max_price": max_price,
            "limit": limit,
            "offset": offset
        }
    )

    return {
        "count": len(df),
        "items": df.to_dict(
            orient="records"
        )
    }

@app.get("/collections")
def collections():
    query = """
    SELECT DISTINCT collection
    FROM products
    ORDER BY collection
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(
        orient="records"
    )

@app.get("/stats")
def stats():

    query = """
    SELECT
        COUNT(*) AS total_products,
        COUNT(DISTINCT collection) AS collections,
        AVG(price_num) AS avg_price,
        MAX(price_num) AS max_price
    FROM products
    """

    df = pd.read_sql(query, engine)

    return {
        "total_products": int(df.iloc[0]["total_products"]),
        "collections": int(df.iloc[0]["collections"]),
        "avg_price": int(df.iloc[0]["avg_price"]),
        "max_price": int(df.iloc[0]["max_price"])
    }