# gui/data.py
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(ROOT_DIR, "logs", "log.txt")


def _parse_kv(text: str) -> str:
    return text.split("=", 1)[1].strip() if "=" in text else text.strip()


# Attempt to import all_nodes from src/config.py so GUI can show nodes
# even when there are no log entries for them yet.
try:
    from config import all_nodes
except Exception:
    all_nodes = {}


def _parse_latency(raw: str):
    """Parse latency string — returns float or None (never the string 'None')."""
    try:
        val = _parse_kv(raw)
        if val.lower() == "none" or val == "":
            return None
        return float(val)
    except (ValueError, TypeError):
        return None


def read_latest_node_states() -> dict:
    states = {}

    # Read existing log entries (if any)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 7:
                    continue
                _, node, ip, state, net, lat, fails, *extra = parts
                ml_prob = None
                if extra:
                    for e in extra:
                        if "ml=" in e:
                            try:
                                val = e.split("=")[1].strip()
                                if val.lower() != "none":
                                    ml_prob = float(val)
                            except Exception:
                                pass

                states[node] = {
                    "ip": ip,
                    "network_type": _parse_kv(net),
                    "state": state,
                    "latency": _parse_latency(lat),  # ← float or None
                    "fails": _parse_kv(fails),
                    "ml_probability": ml_prob,
                }

    # Ensure GUI lists all configured nodes as a fallback when there are
    # no log entries yet for them (use config.all_nodes).
    # In production, the Controller or monitor writes logs, so this fallback
    # is only used on startup before the first heartbeat/ping arrives.
    for node_name, cfg in (all_nodes or {}).items():
        if node_name in states:
            continue
        states[node_name] = {
            "ip": cfg.get("ip"),
            "network_type": cfg.get("network_type", "—"),
            "state": cfg.get("state", "UP"),  # default UP for config state
            "latency": None,
            "fails": "0",
            "ml_probability": None,
        }

    return states


def get_node_latency_history(node_name: str) -> list:
    history = []
    history = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 7 or parts[1] != node_name:
                    continue
                val = _parse_latency(parts[5])
                # For blocked devices or failed pings, use 0 as placeholder
                # This ensures the chart shows data points even when ping fails
                history.append(val if val is not None else 0)

    # Fallback: if no history but node is configured, return a flat zero series
    if not history and (all_nodes or {}).get(node_name) is not None:
        return [0] * 10

    return history[-50:]


def get_global_latency_history() -> list:
    ts_map = {}
    ts_map = {}
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 7:
                    continue
                val = _parse_latency(parts[5])
                if val is not None:
                    ts_map.setdefault(parts[0], []).append(val)

    if not ts_map:
        # If configured nodes exist but no log data yet, show flat zeros
        if all_nodes:
            return [0] * 10
        return []

    return [sum(v) / len(v) for v in (ts_map[t] for t in sorted(ts_map))][-50:]


def get_global_state_distribution() -> tuple:
    up = degraded = down = 0
    node_states = {}  # Track latest state per node
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 4:
                    continue
                node_name = parts[1]
                state = parts[3]
                node_states[node_name] = state

    # If no log-derived states, fall back to configured nodes
    if not node_states and all_nodes:
        for cfg in all_nodes.values():
            s = cfg.get("state", "UNKNOWN")
            if s == "UP":
                up += 1
            elif s == "DEGRADED":
                degraded += 1
            elif s == "DOWN":
                down += 1
        return up, degraded, down

    for state in node_states.values():
        if state == "UP":
            up += 1
        elif state == "DEGRADED":
            degraded += 1
        elif state == "DOWN":
            down += 1

    # Additionally include configured nodes that didn't appear in logs (count by their config state)
    if all_nodes:
        for name, cfg in all_nodes.items():
            if name in node_states:
                continue
            s = cfg.get("state", "UNKNOWN")
            if s == "UP":
                up += 1
            elif s == "DEGRADED":
                degraded += 1
            elif s == "DOWN":
                down += 1

    return up, degraded, down


def get_node_state_distribution(node_name: str) -> tuple:
    up = degraded = down = 0
    found = False
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 7 or parts[1] != node_name:
                    continue
                found = True
                s = parts[3]
                if s == "UP":
                    up += 1
                elif s == "DEGRADED":
                    degraded += 1
                elif s == "DOWN":
                    down += 1

    if not found:
        # Fall back to configured node state if available
        cfg = (all_nodes or {}).get(node_name)
        if cfg is not None:
            s = cfg.get("state", "UNKNOWN")
            if s == "UP":
                up = 1
            elif s == "DEGRADED":
                degraded = 1
            elif s == "DOWN":
                down = 1

    return up, degraded, down
