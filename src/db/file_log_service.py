
# src/db/file_log_service.py
#
# Writes one log line per ping/heartbeat cycle to logs/log.txt.
#
# Format (pipe-delimited, 7 or 8 fields):
#   timestamp | node_name | ip | state | type=<net> | latency=<val> | fails=<n> [| ml=<prob>]
#
# Both monitor.py (real nodes) and controller.py (sim nodes) call this.
# The ml_prob argument is optional — old callers with 6 args still work.

import os
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(ROOT_DIR, "logs", "log.txt")


def write_log_file(
    node_name: str,
    ip: str,
    network_type: str,
    state: str,
    latency,  # float or None
    fail_count: int,
    ml_prob=None,  # float or None — optional
):
    """
    Append one monitoring record to logs/log.txt.
    ml_prob is written as a trailing | ml=<value> field when provided.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lat_str = str(latency) if latency is not None else "None"
    fail_str = str(fail_count)

    line = (
        f"{timestamp} | {node_name} | {ip} | {state} | "
        f"type={network_type} | latency={lat_str} | fails={fail_str}"
    )

    # Append ml= field only when a probability is provided
    if ml_prob is not None:
        try:
            line += f" | ml={float(ml_prob):.4f}"
        except (TypeError, ValueError):
            pass  # skip malformed ml_prob silently

    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")