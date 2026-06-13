from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine

class SearchResponse(BaseModel):
    count: int
    items: list


app = FastAPI()

engine = create_engine(
    "postgresql+psycopg2://sjchoi@localhost/jewelry"
)

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
    limit: int = 20,
    offset: int = 0
):

    order_by = "price ASC"

    if sort == "price_desc":
        order_by = "price DESC"

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
    df = pd.read_sql(
        "SELECT * FROM products",
        engine
    )

    return {
        "total_products": len(df),
        "collections": df["collection"].nunique(),
        "avg_price": int(df["price_num"].mean()),
        "max_price": int(df["price_num"].max())
    }