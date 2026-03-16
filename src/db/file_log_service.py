

import os
from datetime import datetime

# db/ → src/ → root/
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(ROOT_DIR, "logs", "log.txt")


def write_log_file(node_name, ip, network_type, state, latency, fail_count):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = (
        f"{timestamp} | {node_name} | {ip} | "
        f"{state} | type = {network_type} | "
        f"latency={latency} | fails={fail_count}"
    )

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")