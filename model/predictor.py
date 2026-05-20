# predictor.py

import pickle
import pandas as pd
import numpy as np

MODEL_PATH = "/Users/vineetpatel/INTERNSHIP/Project/Network Monitoring & Predictive Failure System/model/modelV3.pkl"
WINDOW = 10


# ==============================
# 🔹 Load Model
# ==============================
def load_model():
    with open(MODEL_PATH, "rb") as f:
        data = pickle.load(f)

    return data["model"], data["features"], data.get("threshold", 0.5)


model, FEATURES, THRESHOLD = load_model()

print("✅ Model loaded successfully")
try:
    importances = model.feature_importances_

    print("\n📊 Feature Importance:")
    for name, imp in sorted(
        zip(FEATURES, importances), key=lambda x: x[1], reverse=True
    ):
        print(f"{name:<25} : {imp:.4f}")

except Exception:
    pass
print(f"📌 Features expected: {len(FEATURES)}")


# ==============================
# 🔹 Feature Builder
# ==============================
def build_features(df):
    df = df.copy()

    # --- Validation ---
    required_cols = [
        "timestamp",
        "latency",
        "fails",
        "state",
        "network_type",
        "node_name",
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"❌ Missing column: {col}")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    df["latency"] = df["latency"].fillna(-1)
    df["ping_failed"] = (df["latency"] == -1).astype(int)
    df["rolling_avg_latency"] = df.groupby("node_name")["latency"].transform(
        lambda x: x.rolling(WINDOW, min_periods=1).mean()
    )

    df["rolling_max_latency"] = df.groupby("node_name")["latency"].transform(
        lambda x: x.rolling(WINDOW, min_periods=1).max()
    )

    df["rolling_std_latency"] = df.groupby("node_name")["latency"].transform(
        lambda x: x.rolling(WINDOW, min_periods=1).std().fillna(0)
    )

    df["latency_trend"] = df.groupby("node_name")["latency"].diff().fillna(0)

    df["latency_acceleration"] = (
        df.groupby("node_name")["latency_trend"].diff().fillna(0)
    )
    df["latency_volatility"] = df.groupby("node_name")["latency"].transform(
        lambda x: x.diff().abs().rolling(WINDOW, min_periods=1).mean()
    )
    df["rolling_fail_sum"] = df.groupby("node_name")["fails"].transform(
        lambda x: x.rolling(WINDOW, min_periods=1).sum()
    )

    df["latency_ratio"] = np.where(
        df["rolling_avg_latency"] > 0,
        df["latency"] / (df["rolling_avg_latency"] + 1e-5),
        0,
    )
    df["fail_rate"] = df["rolling_fail_sum"] / WINDOW

    df["ping_failed_rate"] = df.groupby("node_name")["ping_failed"].transform(
        lambda x: x.rolling(WINDOW, min_periods=1).mean()
    )

    df["is_unstable"] = (
        (df["rolling_std_latency"] > 40) | (df["ping_failed_rate"] > 0.2)
    ).astype(int)

    # --- Time in state ---
    times = []
    last_time = df["timestamp"].iloc[0]
    last_state = df["state"].iloc[0]

    for _, row in df.iterrows():
        if row["state"] != last_state:
            last_time = row["timestamp"]
            last_state = row["state"]
        times.append((row["timestamp"] - last_time).total_seconds())

    df["time_in_state_sec"] = times

    # --- Network encoding ---
    net_map = {"wifi": 0, "router": 1, "ethernet": 2}
    df["network_type_encoded"] = df["network_type"].map(net_map).fillna(3)

    return df


# ==============================
# 🔹 Prediction Function
# ==============================
def predict_failure(df, debug=False):
    df = build_features(df)

    # --- Ensure enough history ---
    if len(df) < WINDOW:
        raise ValueError(f"❌ Not enough data points (need at least {WINDOW} rows)")

    latest = df.iloc[-1]

    missing_features = [f for f in FEATURES if f not in latest.index]

    if missing_features:
        raise ValueError(f"❌ Missing engineered features: {missing_features}")

    # --- Align features safely ---
    X = pd.DataFrame([latest])[FEATURES]

    # --- Predict ---
    prob = model.predict_proba(X)[0][1]
    prediction = int(prob >= THRESHOLD)

    if prob >= 0.8:
        risk = "CRITICAL"
    elif prob >= 0.6:
        risk = "HIGH"
    elif prob >= 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    result = {
        "failure_probability": float(round(prob, 4)),
        "prediction": prediction,
        "risk_level": risk,
        "alert": "🚨 FAILURE RISK!" if prediction else "✅ SAFE",
    }

    if debug:
        print("\n🔍 Debug Info:")
        print(X.T)
        print(f"Threshold: {THRESHOLD}")

    return result


# ==============================
# 🔹 Batch Prediction (NEW)
# ==============================
def predict_batch(df):
    df = build_features(df)
    X = df[FEATURES]

    probs = model.predict_proba(X)[:, 1]
    preds = (probs >= THRESHOLD).astype(int)

    df_result = df.copy()
    df_result["failure_probability"] = probs
    df_result["prediction"] = preds

    return df_result


# ==============================
# 🔹 Compatibility Wrapper
# ==============================
def predict_node_failure(node_data):

    rows = []

    for _ in range(WINDOW):
        rows.append({
        "timestamp": pd.Timestamp.now(),
        "latency": node_data.get("latency", -1),
        "fails": node_data.get("fails", 0),
        "state": node_data.get("state", "UP"),
        "network_type": node_data.get("network_type", "wifi"),
        "node_name": node_data.get("node_name", "live_node")
    })

    df = pd.DataFrame(rows)
    result = predict_failure(df)

    return result["failure_probability"]
