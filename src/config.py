# nodes & constants

LATENCY_THRESHOLD = 100  # ms

nodes = {
    "node_1": {
        "ip": "8.8.8.8",
        "state": "UP",
        "network_type": "wired",
        "fail_count": 0,
        "last_latency": None,
    },
    "node_2": {
        "ip": "1.1.1.1",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
    },
    "node_3": {
        "ip": "9.9.9.9",
        "state": "UP",
        "network_type": "vpn",
        "fail_count": 0,
        "last_latency": None,
    },
}
