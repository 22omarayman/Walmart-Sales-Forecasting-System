from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import time

from core.model_loader import load_model_and_metadata
from core.data_store import load_history
from core.feature_builder import build_row_features

app = FastAPI(title="Sales Forecast API", version="1.0")

class ForecastRequest(BaseModel):
    store: int
    dept: int
    date: str  # YYYY-MM-DD

model = None
meta = None
history = None


@app.on_event("startup")
def startup():
    global model, meta, history
    model, meta = load_model_and_metadata()
    history = load_history()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "history_rows": int(len(history))
    }


@app.get("/model-info")
def model_info():
    feature_cols = meta.get("feature_cols") or meta.get("features") or []
    return {
        "service": {"name": "Sales Forecast API", "version": "1.0"},
        "model": {
            "loaded": model is not None,
            "validation_mae": meta.get("mae"),
            "features_count": len(feature_cols),
            "features": feature_cols
        },
        "data": {
            "history_rows": int(len(history)),
            "history_date_min": str(history["Date"].min().date()),
            "history_date_max": str(history["Date"].max().date())
        }
    }



@app.get("/earliest-valid-date")
def earliest_valid_date(store: int, dept: int, min_history_weeks: int = 8):
    sdf = (
        history[(history["Store"] == store) & (history["Dept"] == dept)]
        .sort_values("Date")
        .reset_index(drop=True)
    )

    if sdf.empty:
        raise HTTPException(status_code=404, detail="No history for this Store/Dept")

    if len(sdf) <= min_history_weeks:
        return {
            "store": store,
            "dept": dept,
            "earliest_safe_date": None,
            "reason": f"Only {len(sdf)} rows available; need > {min_history_weeks} for lag_{min_history_weeks}"
        }

    return {
        "store": store,
        "dept": dept,
        "earliest_safe_date": str(sdf.loc[min_history_weeks, "Date"].date()),
        "rows_available": len(sdf)
    }


@app.get("/compare-next-week")
def compare_next_week(store: int, dept: int, date: str):
    d = pd.to_datetime(date)

    sdf = (
        history[(history["Store"] == store) & (history["Dept"] == dept)]
        .sort_values("Date")
        .reset_index(drop=True)
    )

    idx = sdf.index[sdf["Date"] == d]
    if len(idx) == 0:
        raise HTTPException(status_code=400, detail="Date not found")

    i = int(idx[0])
    if i + 1 >= len(sdf):
        raise HTTPException(status_code=400, detail="No next week available in history")

    # prediction
    row = build_row_features(history, store, dept, date)

    feature_cols = meta.get("feature_cols") or meta.get("features")
    if not feature_cols:
        raise HTTPException(status_code=500, detail="metadata.json missing 'feature_cols' or 'features'")

    X = pd.DataFrame([{c: row[c] for c in feature_cols}])
    yhat = float(model.predict(X)[0])

    y_true = float(sdf.loc[i + 1, "Weekly_Sales"])
    return {
        "date": date,
        "y_true_next_week": y_true,
        "yhat_next_week": yhat,
        "abs_error": abs(y_true - yhat)
    }


@app.post("/forecast-next-week")
def forecast_next_week(req: ForecastRequest):
    start = time.time()

    try:
        row = build_row_features(history, req.store, req.dept, req.date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    feature_cols = meta.get("feature_cols") or meta.get("features")
    if not feature_cols:
        raise HTTPException(status_code=500, detail="metadata.json missing 'feature_cols' or 'features'")

    X = pd.DataFrame([{c: row[c] for c in feature_cols}])
    yhat = float(model.predict(X)[0])

    latency_ms = round((time.time() - start) * 1000, 2)

    return {
        "store": req.store,
        "dept": req.dept,
        "date": req.date,
        "forecast_horizon": "next_week",
        "yhat_weekly_sales": yhat,
        "latency_ms": latency_ms
    }
