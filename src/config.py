# src/config.py

LATENCY_THRESHOLD = 30  # ms — router ~3-5ms normally, >30ms = DEGRADED

nodes = {
    "node_1_phone": {
        "ip": "192.168.1.20",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": True,  # iPhone silently drops ICMP — needs higher fail threshold
    },
    "node_2_laptop": {
        "ip": "192.168.1.19",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
    },
    "node_3_router": {
        "ip": "192.168.1.1",
        "state": "UP",
        "network_type": "router",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
    },
}
