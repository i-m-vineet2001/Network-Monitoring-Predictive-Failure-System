# gui/data.py
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(ROOT_DIR, "logs", "log.txt")


def _parse_kv(text: str) -> str:
    return text.split("=", 1)[1].strip() if "=" in text else text.strip()


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
    if not os.path.exists(LOG_FILE):
        return states

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
                        except:
                            pass

            states[node] = {
                "ip": ip,
                "network_type": _parse_kv(net),
                "state": state,
                "latency": _parse_latency(lat),  # ← float or None
                "fails": _parse_kv(fails),
                "ml_probability": ml_prob,
            }
    return states


def get_node_latency_history(node_name: str) -> list:
    history = []
    if not os.path.exists(LOG_FILE):
        return history

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 7 or parts[1] != node_name:
                continue
            val = _parse_latency(parts[5])
            # For blocked devices or failed pings, use 0 as placeholder
            # This ensures the chart shows data points even when ping fails
            history.append(val if val is not None else 0)

    return history[-50:]


def get_global_latency_history() -> list:
    ts_map = {}
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 7:
                continue
            val = _parse_latency(parts[5])
            if val is not None:
                ts_map.setdefault(parts[0], []).append(val)

    if not ts_map:
        return []
    return [sum(v) / len(v) for v in (ts_map[t] for t in sorted(ts_map))][-50:]


def get_global_state_distribution() -> tuple:
    up = degraded = down = 0
    if not os.path.exists(LOG_FILE):
        return up, degraded, down

    node_states = {}  # Track latest state per node
    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4:
                continue
            node_name = parts[1]
            state = parts[3]
            node_states[node_name] = state

    for state in node_states.values():
        if state == "UP":
            up += 1
        elif state == "DEGRADED":
            degraded += 1
        elif state == "DOWN":
            down += 1

    return up, degraded, down


def get_node_state_distribution(node_name: str) -> tuple:
    up = degraded = down = 0
    if not os.path.exists(LOG_FILE):
        return up, degraded, down

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 7 or parts[1] != node_name:
                continue
            s = parts[3]
            if s == "UP":
                up += 1
            elif s == "DEGRADED":
                degraded += 1
            elif s == "DOWN":
                down += 1

    return up, degraded, down
