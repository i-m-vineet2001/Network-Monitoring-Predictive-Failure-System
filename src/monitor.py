import os
from ping import ping_node
from config import LATENCY_THRESHOLD
from datetime import datetime




def evaluate_status(ping_result: dict, previous_state: str, fail_count: int) -> str:
    if not ping_result["success"]:
        if fail_count >= 3:
            return "DOWN"
        return previous_state

    if ping_result["latency"] is None:
        return "DEGRADED"

    if ping_result["latency"] > LATENCY_THRESHOLD:
        return "DEGRADED"

    return "UP"


def run_monitor(nodes: dict):
    for node_name, node in nodes.items():
        result = ping_node(node["ip"])

        if result["success"]:
            node["fail_count"] = 0
        else:
            node["fail_count"] += 1

        node["state"] = evaluate_status(
            result,
            node["state"],
            node["fail_count"]
        )

        node["last_latency"] = result["latency"]

        print(
            f"{node_name} → {node['state']} | latency={node['last_latency']}"
        )

        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        log_line = (
            f"{time_stamp} | {node_name} | {node['ip']} | "
            f"{node['state']} | "
            f"type = {node['network_type']} | "
            f"latency={node['last_latency']} | "
            f"fails={node['fail_count']}"
        )

        write_log(log_line)



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "logs", "log.txt")

def write_log(message: str):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")
