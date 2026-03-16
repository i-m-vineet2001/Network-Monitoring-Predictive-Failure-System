# # src/monitor.py
# import os
# import sys
# from datetime import datetime

# SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR = os.path.dirname(SRC_DIR)
# sys.path.insert(0, SRC_DIR)
# sys.path.insert(0, ROOT_DIR)

# from config import LATENCY_THRESHOLD
# from db.log_service import insert_log
# from db.file_log_service import write_log_file

# LOG_FILE = os.path.join(ROOT_DIR, "logs", "log.txt")

# FAIL_THRESHOLD_NORMAL = 3  # normal nodes: DOWN after 3 consecutive failures
# FAIL_THRESHOLD_BLOCKED = 8  # iPhone: DOWN after 8 failures (~40s) — avoids false DOWN


# def evaluate_status(
#     ping_result: dict, previous_state: str, fail_count: int, ping_blocked: bool = False
# ) -> str:
#     if not ping_result["success"]:
#         threshold = FAIL_THRESHOLD_BLOCKED if ping_blocked else FAIL_THRESHOLD_NORMAL
#         return "DOWN" if fail_count >= threshold else previous_state

#     latency = ping_result.get("latency")
#     if latency is None:
#         return "UP"  # ping succeeded, just no latency data
#     if latency > LATENCY_THRESHOLD:
#         return "DEGRADED"
#     return "UP"


# def _fallback_write(line: str):
#     os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
#     with open(LOG_FILE, "a") as f:
#         f.write(line + "\n")


# def run_monitor(nodes: dict):
#     try:
#         from ping import ping_node
#     except ImportError:
#         print("[WARN] ping.py not found — skipping cycle")
#         return

#     for node_name, node in nodes.items():
#         ping_blocked = node.get("ping_blocked", False)
#         result = ping_node(node["ip"], ping_blocked=ping_blocked)
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         if result["success"]:
#             node["fail_count"] = 0
#         else:
#             node["fail_count"] += 1

#         node["state"] = evaluate_status(
#             result, node["state"], node["fail_count"], ping_blocked
#         )
#         node["last_latency"] = result.get("latency")

#         print(
#             f"[{timestamp}] {node_name} → {node['state']} "
#             f"| latency={node['last_latency']} ms | fails={node['fail_count']}"
#         )

#         try:
#             write_log_file(
#                 node_name,
#                 node["ip"],
#                 node["network_type"],
#                 node["state"],
#                 node["last_latency"],
#                 node["fail_count"],
#             )
#         except Exception as exc:
#             line = (
#                 f"{timestamp} | {node_name} | {node['ip']} | "
#                 f"{node['state']} | type = {node['network_type']} | "
#                 f"latency={node['last_latency']} | fails={node['fail_count']}"
#             )
#             _fallback_write(line)
#             print(f"[WARN] file_log_service failed ({exc}), used fallback")

#         insert_log(
#             node_name,
#             node["ip"],
#             node["network_type"],
#             node["state"],
#             node["last_latency"],
#             node["fail_count"],
#         )







# src/monitor.py
import os
import sys
from datetime import datetime

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from config import LATENCY_THRESHOLD
from db.log_service import insert_log
from db.file_log_service import write_log_file

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

        print(
            f"[{timestamp}] {node_name} → {node['state']} "
            f"| latency={node['last_latency']} ms | fails={node['fail_count']}"
        )

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
            line = (
                f"{timestamp} | {node_name} | {node['ip']} | "
                f"{node['state']} | type={node['network_type']} | "
                f"latency={node['last_latency']} | fails={node['fail_count']}"
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