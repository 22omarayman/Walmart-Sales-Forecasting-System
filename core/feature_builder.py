import pandas as pd
import numpy as np

def build_row_features(history, store, dept, date):
    date = pd.to_datetime(date)

    sdf = history[(history["Store"] == store) & (history["Dept"] == dept)].copy()
    if sdf.empty:
        raise ValueError("No history found for this Store/Dept.")

    sdf = sdf.sort_values("Date").reset_index(drop=True)

    idx = sdf.index[sdf["Date"] == date]
    if len(idx) == 0:
        raise ValueError("Date not found in history for this Store/Dept. Use a date that exists in the dataset.")
    i = int(idx[0])

    def lag(k):
        j = i - k
        return float(sdf.loc[j, "Weekly_Sales"]) if j >= 0 else np.nan

    sales = sdf["Weekly_Sales"].astype(float).values

    def roll_mean(win):
        start = i - win
        end = i
        if start < 0:
            return np.nan
        return float(np.mean(sales[start:end]))

    row = sdf.loc[i].to_dict()

    ts = pd.Timestamp(row["Date"])
    row["week"] = int(ts.isocalendar().week)
    row["month"] = int(ts.month)
    row["year"] = int(ts.year)
    row["is_weekend"] = int(ts.dayofweek >= 5)

    row["lag_1"] = lag(1)
    row["lag_2"] = lag(2)
    row["lag_4"] = lag(4)
    row["lag_8"] = lag(8)
    row["roll_mean_4"] = roll_mean(4)
    row["roll_mean_8"] = roll_mean(8)

    needed = ["lag_1","lag_2","lag_4","lag_8","roll_mean_4","roll_mean_8"]
    if any(pd.isna(row[k]) for k in needed):
        raise ValueError("Not enough past weeks to compute lag/rolling features for this date.")

    return row
