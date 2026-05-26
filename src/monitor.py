


# NEW CODE
# src/monitor.py
#
# Changes vs previous version (everything else unchanged):
#
#   + _history  dict: rolling deque of last 10 readings per node
#   + After each ping cycle, calls predictor.predict_node_failure_from_buffer()
#   + Attaches ml result to node dict (node['ml_result'])
#   + Writes ml=<probability> as extra field in log line
#   + ML alert fires if risk changes to HIGH/CRITICAL (spam guard via last_ml_alert)
#   + If predictor import fails, monitoring continues normally (safe fallback)

import os
import sys
from collections import deque
from datetime import datetime

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from config import LATENCY_THRESHOLD
from db.log_service import insert_log
from db.file_log_service import write_log_file

LOG_FILE = os.path.join(ROOT_DIR, "logs", "log.txt")

FAIL_THRESHOLD_NORMAL = 3
FAIL_THRESHOLD_BLOCKED = 8

# ── ML predictor (optional — falls back gracefully if not available) ───
_predictor_available = False
try:
    MODEL_DIR = os.path.join(ROOT_DIR, "model")
    sys.path.insert(0, MODEL_DIR)
    from predictor import predict_node_failure_from_buffer

    _predictor_available = True
    print("[Monitor] ✅ ML predictor loaded")
except Exception as e:
    print(f"[Monitor] ⚠️  ML predictor not available: {e}")

    def predict_node_failure_from_buffer(*args, **kwargs):
        return {
            "failure_probability": 0.0,
            "prediction": 0,
            "risk_level": "LOW",
            "alert": "N/A",
            "enough_data": False,
        }


# ── Rolling history buffer (WINDOW=10 per node) ────────────────────────
HISTORY_WINDOW = 10
_history: dict = {}  # node_name → deque of dicts


def _get_history(node_name: str) -> deque:
    if node_name not in _history:
        _history[node_name] = deque(maxlen=HISTORY_WINDOW)
    return _history[node_name]


# ── State evaluation (unchanged) ──────────────────────────────────────
def evaluate_status(
    ping_result: dict, previous_state: str, fail_count: int, ping_blocked: bool = False
) -> str:
    if not ping_result["success"]:
        threshold = FAIL_THRESHOLD_BLOCKED if ping_blocked else FAIL_THRESHOLD_NORMAL
        if previous_state == "DOWN":
            return "DOWN"
        return "DOWN" if fail_count >= threshold else previous_state

    latency = ping_result.get("latency")
    if latency is None:
        return "UP"
    return "DEGRADED" if latency > LATENCY_THRESHOLD else "UP"


def _fallback_write(line: str):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ── Main monitor loop ──────────────────────────────────────────────────
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

        # ── Update state ──────────────────────────────────────────────
        if result["success"]:
            node["fail_count"] = 0
        else:
            node["fail_count"] += 1

        node["state"] = evaluate_status(
            result, node["state"], node["fail_count"], ping_blocked
        )
        node["last_latency"] = result.get("latency")

        # ── ML prediction ─────────────────────────────────────────────
        hist = _get_history(node_name)
        hist.append(
            {
                "timestamp": timestamp,
                "latency": node["last_latency"],
                "fails": node["fail_count"],
                "state": node["state"],
            }
        )

        ml = predict_node_failure_from_buffer(
            node_name=node_name,
            buffer=list(hist),
            network_type=node.get("network_type", "wifi"),
        )
        node["ml_result"] = ml  # GUI can read this from node dict

        ml_prob = ml["failure_probability"]
        ml_risk = ml["risk_level"]

        # ── Terminal output ───────────────────────────────────────────
        print(
            f"[{timestamp}] {node_name} → {node['state']:8s} "
            f"| lat={node['last_latency']} ms "
            f"| fails={node['fail_count']} "
            f"| ml={ml_prob:.2f} ({ml_risk})"
        )

        # ── ML alert spam guard ───────────────────────────────────────
        # Only print a warning when risk level CHANGES to HIGH or CRITICAL
        prev_alert = node.get("last_ml_alert")
        if ml_risk in ("HIGH", "CRITICAL") and prev_alert != ml_risk:
            print(
                f"  ⚠️  [{node_name}] ML ALERT: {ml['alert']} — risk={ml_risk} ({ml_prob:.2f})"
            )
        node["last_ml_alert"] = ml_risk

        # ── File log (adds ml= field at the end) ─────────────────────
        try:
            write_log_file(
                node_name,
                node["ip"],
                node["network_type"],
                node["state"],
                node["last_latency"],
                node["fail_count"],
                ml_prob,  # passed as extra arg → handled below
            )
        except TypeError:
            # Old write_log_file doesn't accept ml_prob — fallback
            try:
                write_log_file(
                    node_name,
                    node["ip"],
                    node["network_type"],
                    node["state"],
                    node["last_latency"],
                    node["fail_count"],
                )
            except Exception as exc:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                line = (
                    f"{ts} | {node_name} | {node['ip']} | "
                    f"{node['state']} | type={node['network_type']} | "
                    f"latency={node['last_latency']} | fails={node['fail_count']} | "
                    f"ml={ml_prob}"
                )
                _fallback_write(line)
                print(f"[WARN] file_log_service failed ({exc}), used fallback")
        except Exception as exc:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            line = (
                f"{ts} | {node_name} | {node['ip']} | "
                f"{node['state']} | type={node['network_type']} | "
                f"latency={node['last_latency']} | fails={node['fail_count']} | "
                f"ml={ml_prob}"
            )
            _fallback_write(line)
            print(f"[WARN] file_log_service failed ({exc}), used fallback")

        # ── MongoDB log (unchanged) ───────────────────────────────────
        insert_log(
            node_name,
            node["ip"],
            node["network_type"],
            node["state"],
            node["last_latency"],
            node["fail_count"],
        )