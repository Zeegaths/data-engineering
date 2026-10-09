import os
import time
import socket
import urllib3.util.connection as urllib3_cn

urllib3_cn.allowed_gai_family = lambda: socket.AF_INET
import pandas as pd
import requests
from sqlalchemy import create_engine, text

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "crypto")

API_URL = "https://blockstream.info/api/blocks"
TABLE = "btc_blocks"


def extract():
    print(f"Fetching {API_URL}")
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return pd.DataFrame(r.json())


def transform(df):
    cols = ["id", "height", "timestamp", "tx_count", "size",
            "weight", "difficulty", "nonce", "previousblockhash"]
    df = df[cols].rename(columns={
        "id": "block_hash",
        "size": "size_bytes",
        "previousblockhash": "prev_block_hash",
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["size_mb"] = (df["size_bytes"] / 1_000_000).round(3)
    df = df.drop_duplicates(subset="block_hash").dropna()
    return df.sort_values("height").reset_index(drop=True)


def get_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(url)
    for attempt in range(1, 11):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"Connected to Postgres at {DB_HOST}")
            return engine
        except Exception as e:
            print(f"DB not ready (attempt {attempt}): {e}")
            time.sleep(3)
    raise RuntimeError("Could not connect to Postgres")


def load(df, engine):
    df.to_sql(TABLE, engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into {TABLE}")


if __name__ == "__main__":
    raw = extract()
    clean = transform(raw)
    print(clean.head())
    load(clean, get_engine())
