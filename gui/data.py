# gui/data.py
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "log.txt")


def parse_key_value(text):
    if "=" not in text:
        return text.strip()

    return text.split("=", 1)[1].strip()


# Latest state per node
def read_latest_node_states():

    states = {}

    if not os.path.exists(LOG_FILE):
        return states

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]

            if len(parts) != 7:
                continue

            # CORRECT ORDER: timestamp | node | ip | state | type | latency | fails
            timestamp = parts[0]
            node = parts[1]
            ip = parts[2]
            state = parts[3]
            network_type = parse_key_value(parts[4])
            latency = parse_key_value(parts[5])
            fails = parse_key_value(parts[6])

            states[node] = {
                "ip": ip,
                "network_type": network_type,
                "state": state,
                "latency": latency,
                "fails": fails,
            }

    return states


# Latency history per node
def get_node_latency_history(node_name):

    history = []

    if not os.path.exists(LOG_FILE):
        return history

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]

            if len(parts) != 7:
                continue

            node = parts[1]

            if node != node_name:
                continue

            latency = parse_key_value(parts[5])

            try:
                history.append(float(latency))
            except:
                pass

    return history[-50:]



# Global latency history
def get_global_latency_history():

    timestamp_map = {}

    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]

            if len(parts) != 7:
                continue

            timestamp = parts[0]
            latency = parse_key_value(parts[5])

            try:
                latency = float(latency)
            except:
                continue

            timestamp_map.setdefault(timestamp, []).append(latency)

    history = []

    for t in sorted(timestamp_map.keys()):
        values = timestamp_map[t]
        history.append(sum(values) / len(values))

    return history[-50:]



# State distribution per node
def get_node_state_distribution(node_name):

    up = 0
    degraded = 0
    down = 0

    if not os.path.exists(LOG_FILE):
        return up, degraded, down

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]

            if len(parts) != 7:
                continue

            node = parts[1]
            state = parts[3]

            if node != node_name:
                continue

            if state == "UP":
                up += 1

            elif state == "DEGRADED":
                degraded += 1

            elif state == "DOWN":
                down += 1

    return up, degraded, down
