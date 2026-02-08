import json
import joblib
from pathlib import Path

def load_model_and_metadata():
    root = Path(__file__).resolve().parents[1]   # project root
    art_dir = root / "artifacts"

    model_path = art_dir / "model.joblib"
    meta_path = art_dir / "metadata.json"

    model = joblib.load(model_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return model, meta
