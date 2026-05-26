# # predictor.py

# import pickle
# import pandas as pd
# import numpy as np

# MODEL_PATH = "/Users/vineetpatel/INTERNSHIP/Project/Network Monitoring & Predictive Failure System/model/modelV3.pkl"
# WINDOW = 10


# # ==============================
# # 🔹 Load Model
# # ==============================
# def load_model():
#     with open(MODEL_PATH, "rb") as f:
#         data = pickle.load(f)

#     return data["model"], data["features"], data.get("threshold", 0.5)


# model, FEATURES, THRESHOLD = load_model()

# print("✅ Model loaded successfully")
# try:
#     importances = model.feature_importances_

#     print("\n📊 Feature Importance:")
#     for name, imp in sorted(
#         zip(FEATURES, importances), key=lambda x: x[1], reverse=True
#     ):
#         print(f"{name:<25} : {imp:.4f}")

# except Exception:
#     pass
# print(f"📌 Features expected: {len(FEATURES)}")


# # ==============================
# # 🔹 Feature Builder
# # ==============================
# def build_features(df):
#     df = df.copy()

#     # --- Validation ---
#     required_cols = [
#         "timestamp",
#         "latency",
#         "fails",
#         "state",
#         "network_type",
#         "node_name",
#     ]
#     for col in required_cols:
#         if col not in df.columns:
#             raise ValueError(f"❌ Missing column: {col}")

#     df["timestamp"] = pd.to_datetime(df["timestamp"])
#     df = df.sort_values("timestamp")

#     df["latency"] = df["latency"].fillna(-1)
#     df["ping_failed"] = (df["latency"] == -1).astype(int)
#     df["rolling_avg_latency"] = df.groupby("node_name")["latency"].transform(
#         lambda x: x.rolling(WINDOW, min_periods=1).mean()
#     )

#     df["rolling_max_latency"] = df.groupby("node_name")["latency"].transform(
#         lambda x: x.rolling(WINDOW, min_periods=1).max()
#     )

#     df["rolling_std_latency"] = df.groupby("node_name")["latency"].transform(
#         lambda x: x.rolling(WINDOW, min_periods=1).std().fillna(0)
#     )

#     df["latency_trend"] = df.groupby("node_name")["latency"].diff().fillna(0)

#     df["latency_acceleration"] = (
#         df.groupby("node_name")["latency_trend"].diff().fillna(0)
#     )
#     df["latency_volatility"] = df.groupby("node_name")["latency"].transform(
#         lambda x: x.diff().abs().rolling(WINDOW, min_periods=1).mean()
#     )
#     df["rolling_fail_sum"] = df.groupby("node_name")["fails"].transform(
#         lambda x: x.rolling(WINDOW, min_periods=1).sum()
#     )

#     df["latency_ratio"] = np.where(
#         df["rolling_avg_latency"] > 0,
#         df["latency"] / (df["rolling_avg_latency"] + 1e-5),
#         0,
#     )
#     df["fail_rate"] = df["rolling_fail_sum"] / WINDOW

#     df["ping_failed_rate"] = df.groupby("node_name")["ping_failed"].transform(
#         lambda x: x.rolling(WINDOW, min_periods=1).mean()
#     )

#     df["is_unstable"] = (
#         (df["rolling_std_latency"] > 40) | (df["ping_failed_rate"] > 0.2)
#     ).astype(int)

#     # --- Time in state ---
#     times = []
#     last_time = df["timestamp"].iloc[0]
#     last_state = df["state"].iloc[0]

#     for _, row in df.iterrows():
#         if row["state"] != last_state:
#             last_time = row["timestamp"]
#             last_state = row["state"]
#         times.append((row["timestamp"] - last_time).total_seconds())

#     df["time_in_state_sec"] = times

#     # --- Network encoding ---
#     net_map = {"wifi": 0, "router": 1, "ethernet": 2}
#     df["network_type_encoded"] = df["network_type"].map(net_map).fillna(3)

#     return df


# # ==============================
# # 🔹 Prediction Function
# # ==============================
# def predict_failure(df, debug=False):
#     df = build_features(df)

#     # --- Ensure enough history ---
#     if len(df) < WINDOW:
#         raise ValueError(f"❌ Not enough data points (need at least {WINDOW} rows)")

#     latest = df.iloc[-1]

#     missing_features = [f for f in FEATURES if f not in latest.index]

#     if missing_features:
#         raise ValueError(f"❌ Missing engineered features: {missing_features}")

#     # --- Align features safely ---
#     X = pd.DataFrame([latest])[FEATURES]

#     # --- Predict ---
#     prob = model.predict_proba(X)[0][1]
#     prediction = int(prob >= THRESHOLD)

#     if prob >= 0.8:
#         risk = "CRITICAL"
#     elif prob >= 0.6:
#         risk = "HIGH"
#     elif prob >= 0.4:
#         risk = "MEDIUM"
#     else:
#         risk = "LOW"
#     result = {
#         "failure_probability": float(round(prob, 4)),
#         "prediction": prediction,
#         "risk_level": risk,
#         "alert": "🚨 FAILURE RISK!" if prediction else "✅ SAFE",
#     }

#     if debug:
#         print("\n🔍 Debug Info:")
#         print(X.T)
#         print(f"Threshold: {THRESHOLD}")

#     return result


# # ==============================
# # 🔹 Batch Prediction (NEW)
# # ==============================
# def predict_batch(df):
#     df = build_features(df)
#     X = df[FEATURES]

#     probs = model.predict_proba(X)[:, 1]
#     preds = (probs >= THRESHOLD).astype(int)

#     df_result = df.copy()
#     df_result["failure_probability"] = probs
#     df_result["prediction"] = preds

#     return df_result


# # ==============================
# # 🔹 Compatibility Wrapper
# # ==============================
# def predict_node_failure(node_data):

#     rows = []

#     for _ in range(WINDOW):
#         rows.append({
#         "timestamp": pd.Timestamp.now(),
#         "latency": node_data.get("latency", -1),
#         "fails": node_data.get("fails", 0),
#         "state": node_data.get("state", "UP"),
#         "network_type": node_data.get("network_type", "wifi"),
#         "node_name": node_data.get("node_name", "live_node")
#     })

#     df = pd.DataFrame(rows)
#     result = predict_failure(df)

#     return result["failure_probability"]










# NEW CODE

# model/predictor.py
#
# Loads modelV3.pkl and exposes two functions:
#
#   predict_node_failure(history_df)  ← called by monitor.py every cycle
#   predict_node_failure_from_buffer(node_name, buffer) ← convenience wrapper
#
# monitor.py keeps a rolling deque of the last 10 readings per node.
# It passes that deque (as a list of dicts) to predict_node_failure_from_buffer().
# The result dict is attached to the node and written to the log.
#
# This file does NOT import anything from gui/ or src/ — it is self-contained.

import os
import sys
import pickle
import warnings
import numpy as np
import pandas as pd
from collections import deque

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_THIS_DIR)
MODEL_FILE = os.path.join(_THIS_DIR, "modelV3.pkl")

WINDOW = 10  # must match the value used during training


# ── Load model once at import time ─────────────────────────────────────
def _load():
    if not os.path.exists(MODEL_FILE):
        print(f"[Predictor] ⚠️  Model file not found: {MODEL_FILE}")
        return None, None, 0.4
    try:
        with open(MODEL_FILE, "rb") as f:
            data = pickle.load(f)
        m = data["model"]
        feat = data["features"]
        thr = data.get("threshold", 0.4)
        print(f"[Predictor] ✅ modelV3 loaded — {len(feat)} features, threshold={thr}")
        return m, feat, thr
    except Exception as e:
        print(f"[Predictor] ❌ Failed to load model: {e}")
        return None, None, 0.4


_model, FEATURES, THRESHOLD = _load()


# ── Internal feature builder ───────────────────────────────────────────
def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame with columns:
      timestamp, node_name, latency, fails, state, network_type
    Returns the same DataFrame with all 14 engineered features added.
    Mirrors exactly the feature engineering in n_w_model.py.
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Ping failed flag (latency=None → -1 → ping_failed=1)
    df["latency"] = df["latency"].fillna(-1).astype(float)
    df["ping_failed"] = (df["latency"] == -1).astype(int)

    # Rolling latency stats
    df["rolling_avg_latency"] = df["latency"].rolling(WINDOW, min_periods=1).mean()
    df["rolling_max_latency"] = df["latency"].rolling(WINDOW, min_periods=1).max()
    df["rolling_std_latency"] = (
        df["latency"].rolling(WINDOW, min_periods=1).std().fillna(0)
    )

    # Trend features
    df["latency_trend"] = df["latency"].diff().fillna(0)
    df["latency_acceleration"] = df["latency_trend"].diff().fillna(0)
    df["latency_volatility"] = (
        df["latency"].diff().abs().rolling(WINDOW, min_periods=1).mean().fillna(0)
    )

    # Fail features
    df["rolling_fail_sum"] = df["fails"].rolling(WINDOW, min_periods=1).sum()
    df["fail_rate"] = df["rolling_fail_sum"] / WINDOW

    # Ratio
    df["latency_ratio"] = np.where(
        df["rolling_avg_latency"] > 0,
        df["latency"] / (df["rolling_avg_latency"] + 1e-5),
        0,
    )

    # Ping-fail rate
    df["ping_failed_rate"] = df["ping_failed"].rolling(WINDOW, min_periods=1).mean()

    # Instability flag
    df["is_unstable"] = (
        (df["rolling_std_latency"] > 40) | (df["ping_failed_rate"] > 0.2)
    ).astype(int)

    # Time in state (seconds)
    times = []
    last_time = df["timestamp"].iloc[0]
    last_state = df["state"].iloc[0]
    for _, row in df.iterrows():
        if row["state"] != last_state:
            last_time = row["timestamp"]
            last_state = row["state"]
        times.append((row["timestamp"] - last_time).total_seconds())
    df["time_in_state_sec"] = times

    # Network type encoding
    net_map = {"wifi": 0, "router": 1, "ethernet": 2}
    df["network_type_encoded"] = df["network_type"].map(net_map).fillna(3).astype(int)

    return df


# ── Public API ─────────────────────────────────────────────────────────


def predict_node_failure(history_df: pd.DataFrame) -> dict:
    """
    Main prediction function.

    Parameters
    ----------
    history_df : pd.DataFrame
        Last N readings for ONE node with columns:
          timestamp, node_name, latency, fails, state, network_type
        Needs at least WINDOW (10) rows for reliable results.
        Works with fewer rows (uses min_periods=1) but accuracy is lower.

    Returns
    -------
    dict with keys:
        failure_probability  float 0-1
        prediction           int   0=safe, 1=failure likely
        risk_level           str   LOW / MEDIUM / HIGH / CRITICAL
        alert                str   human-readable message
        enough_data          bool  True if >= WINDOW rows provided
    """
    # Model not loaded — return safe default so monitor still runs
    if _model is None:
        return {
            "failure_probability": 0.0,
            "prediction": 0,
            "risk_level": "LOW",
            "alert": "⚠️ Model not loaded",
            "enough_data": False,
        }

    try:
        enough = len(history_df) >= WINDOW
        df = _build_features(history_df)
        latest = df.iloc[[-1]][FEATURES]

        prob = float(_model.predict_proba(latest)[0][1])
        prediction = int(prob >= THRESHOLD)

        if prob >= 0.8:
            risk = "CRITICAL"
        elif prob >= 0.6:
            risk = "HIGH"
        elif prob >= 0.4:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "failure_probability": round(prob, 4),
            "prediction": prediction,
            "risk_level": risk,
            "alert": "🚨 FAILURE RISK!" if prediction else "✅ SAFE",
            "enough_data": enough,
        }

    except Exception as e:
        return {
            "failure_probability": 0.0,
            "prediction": 0,
            "risk_level": "LOW",
            "alert": f"⚠️ Prediction error: {e}",
            "enough_data": False,
        }


def predict_node_failure_from_buffer(
    node_name: str, buffer: list, network_type: str = "wifi"
) -> dict:
    """
    Convenience wrapper for monitor.py.

    Parameters
    ----------
    node_name    : str   — node key from config.py
    buffer       : list  — list of dicts, each dict is one ping reading:
                           { timestamp, latency, fails, state }
                           (latency=None is fine, handled internally)
    network_type : str   — 'wifi' / 'router' / 'ethernet'

    Returns the same dict as predict_node_failure().
    """
    if not buffer:
        return {
            "failure_probability": 0.0,
            "prediction": 0,
            "risk_level": "LOW",
            "alert": "⚠️ No data yet",
            "enough_data": False,
        }

    rows = []
    for entry in buffer:
        rows.append(
            {
                "timestamp": entry.get("timestamp"),
                "node_name": node_name,
                "latency": entry.get("latency"),  # None is handled
                "fails": entry.get("fails", 0),
                "state": entry.get("state", "UP"),
                "network_type": network_type,
            }
        )

    df = pd.DataFrame(rows)
    return predict_node_failure(df)