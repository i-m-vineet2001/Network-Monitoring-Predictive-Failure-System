# src/monitor.py
import os
import sys
from datetime import datetime
import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from config import LATENCY_THRESHOLD
from db.log_service import insert_log
from db.file_log_service import write_log_file

# Import ML predictor
try:
    from model.predictor import predict_node_failure

    ML_AVAILABLE = True
except ImportError:
    print("[WARN] ML predictor not available")
    ML_AVAILABLE = False


def predict_node_failure_fallback(x):
    return None


if not ML_AVAILABLE:
    predict_node_failure = predict_node_failure_fallback


def predict_failure(df):
    """Wrapper to use predict_node_failure with DataFrame"""
    if not ML_AVAILABLE or df.empty:
        return {"failure_probability": 0.1}

    # Get latest data
    latest = df.iloc[-1]
    node_data = {
        "latency": latest.get("latency", 0),
        "fails": latest.get("fails", 0),
        "state": latest.get("state", "UP"),
        "network_type": latest.get("network_type", "wifi"),
        "recent_latencies": df["latency"].tolist(),
        "recent_fails": df["fails"].tolist(),
        "recent_states": df["state"].tolist(),
    }
    prob = predict_node_failure(node_data)
    return {"failure_probability": prob if prob is not None else 0.1}


LOG_FILE = os.path.join(ROOT_DIR, "logs", "log.txt")

FAIL_THRESHOLD_NORMAL = 3  # non-blocked nodes: DOWN after 3 fails (~15s)
FAIL_THRESHOLD_BLOCKED = 8  # iPhone: DOWN after 8 fails (~40s) — avoids false DOWN


def evaluate_status(
    ping_result: dict,
    previous_state: str,
    fail_count: int,
    ping_blocked: bool = False,
) -> str:
    """
    Determine node state from the latest ping result.

    On failure:  stay in previous_state until fail_count hits threshold, then DOWN.
    On success:  always UP or DEGRADED — never stuck in DOWN after recovery.
    """
    if not ping_result["success"]:
        threshold = FAIL_THRESHOLD_BLOCKED if ping_blocked else FAIL_THRESHOLD_NORMAL
        # Once already DOWN keep it DOWN; otherwise hold previous until threshold
        if previous_state == "DOWN":
            return "DOWN"
        return "DOWN" if fail_count >= threshold else previous_state

    # ── ping succeeded: always escape DOWN/DEGRADED immediately ──
    # fail_count is already reset to 0 in run_monitor before this call
    latency = ping_result.get("latency")
    if latency is None:
        return "UP"
    if latency > LATENCY_THRESHOLD:
        return "DEGRADED"
    return "UP"


def _fallback_write(line: str):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_monitor(nodes: dict):
    try:
        from ping import ping_node
    except ImportError:
        print("[WARN] ping.py not found — skipping cycle")
        return

    for node_name, node in nodes.items():
        ping_blocked = node.get("ping_blocked", False)
        result = ping_node(node["ip"], ping_blocked=ping_blocked)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Reset fail_count BEFORE evaluate_status so recovery is instant
        if result["success"]:
            node["fail_count"] = 0
        else:
            node["fail_count"] += 1

        node["state"] = evaluate_status(
            result, node["state"], node["fail_count"], ping_blocked
        )
        node["last_latency"] = result.get("latency")
        # ==============================
        # 🔹 ML HISTORY BUFFER (ADD HERE)
        # ==============================
        node.setdefault("history", [])
        lat = node["last_latency"] if node["last_latency"] is not None else -1

        node["history"].append(
            {
                "timestamp": datetime.now(),
                "latency": lat,
                "fails": node["fail_count"],
                "state": node["state"],
                "network_type": node["network_type"],
                "node_name": node_name,
                "ping_failed": 1 if result["success"] is False else 0,
            }
        )
        # keep last 15 entries (sliding window)
        node["history"] = node["history"][-30:]

        # ==============================
        # 🔹 REAL-TIME ML PREDICTION
        # ==============================
        if len(node["history"]) >= 5:
            try:
                df = pd.DataFrame(node["history"])
                ml_result = predict_failure(df)

                new_prob = float(ml_result["failure_probability"])
                prev_prob = node.get("ml_probability")
                if prev_prob is None:
                    prev_prob = new_prob

                # Smooth prediction (stabilizes + improves reaction)
                node["ml_probability"] = 0.4 * prev_prob + 0.6 * new_prob

            except Exception:
                node["ml_probability"] = None
        else:
            node["ml_probability"] = None

        if node["state"] == "DOWN":
            if node.get("ml_probability") is not None:
                node["ml_probability"] = max(node["ml_probability"], 0.8)
            else:
                node["ml_probability"] = 0.8

        # Determine ML alert level and avoid spamming
        current_prob = node.get("ml_probability")
        if current_prob is None:
            alert_level = "none"
        elif current_prob >= 0.8:
            alert_level = "critical"
        elif current_prob >= 0.6:
            alert_level = "high"
        elif current_prob >= 0.3:
            alert_level = "medium"
        else:
            alert_level = "low"

        last_alert = node.get("last_ml_alert")
        if alert_level != last_alert and alert_level != "none":
            # Only log when alert level changes and it's not none
            print(
                f"🚨 ML ALERT: {node_name} failure risk is {alert_level.upper()} ({current_prob:.1f})"
            )
            node["last_ml_alert"] = alert_level
        elif last_alert and alert_level == "none":
            # Reset when prediction becomes none
            node["last_ml_alert"] = None

        print(f"ML → {node_name}: {current_prob} ({alert_level})")

        # Format latency display - always show a value
        if node["last_latency"] is not None:
            latency_display = f"{node['last_latency']:.1f} ms"
        elif result.get("error") == "ping_blocked":
            latency_display = "0 ms"  # Show 0 for blocked devices
        else:
            latency_display = "0 ms"  # Show 0 for failed pings

        print(
            f"[{timestamp}] {node_name} → {node['state']} "
            f"| latency={latency_display} | fails={node['fail_count']} | ml={node.get('ml_probability', 'N/A')}"
        )

        try:
            write_log_file(
                node_name,
                node["ip"],
                node["network_type"],
                node["state"],
                node["last_latency"],
                node["fail_count"],
                ml_prob=node.get("ml_probability"),
            )
        except Exception as exc:
            line = (
                f"{timestamp} | {node_name} | {node['ip']} | "
                f"{node['state']} | type={node['network_type']} | "
                f"latency={node['last_latency']} | fails={node['fail_count']} | "
                f"ml={node.get('ml_probability')}"
            )
            _fallback_write(line)
            print(f"[WARN] file_log_service failed ({exc}), used fallback")

        insert_log(
            node_name,
            node["ip"],
            node["network_type"],
            node["state"],
            node["last_latency"],
            node["fail_count"],
        )
