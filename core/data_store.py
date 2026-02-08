from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]  # project root
DATA_PATH = ROOT / "data" / "history.parquet"

TYPE_MAP = {"A": 0, "B": 1, "C": 2}

MARKDOWN_COLS = ["MarkDown1","MarkDown2","MarkDown3","MarkDown4","MarkDown5"]

def load_history():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"history.parquet not found at: {DATA_PATH}")

    df = pd.read_parquet(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    for c in MARKDOWN_COLS:
        if c in df.columns:
            df[c] = df[c].fillna(0.0)

    if "Type" in df.columns:
        if pd.api.types.is_numeric_dtype(df["Type"]):
            df["Type"] = df["Type"].fillna(df["Type"].mode()[0]).astype(int)
        else:
            df["Type"] = df["Type"].astype(str).str.strip().str.upper().map(TYPE_MAP)
            df["Type"] = df["Type"].fillna(df["Type"].mode()[0]).astype(int)

    df = df.sort_values(["Store", "Dept", "Date"]).reset_index(drop=True)
    return df
