from fastapi import FastAPI
from sqlalchemy import create_engine
import pandas as pd

app = FastAPI()

engine = create_engine(
    "postgresql+psycopg2://sjchoi@localhost/jewelry"
)

@app.get("/search")
def search(keyword: str):

    df = pd.read_sql(
        "SELECT * FROM products",
        engine
    )

    result = df[
        df["name"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]

    return result.to_dict(
        orient="records"
    )