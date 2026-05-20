# src/config.py

LATENCY_THRESHOLD = 30  # ms — router ~3-5ms normally, >30ms = DEGRADED

nodes = {
    "node_1_phone1": {
        "ip": "192.168.1.33",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": True,  # iPhone silently drops ICMP — needs higher fail threshold
        "last_ml_alert": None,  # Track last ML alert level to avoid spam
    },
    "node_2_laptop": {
        "ip": "192.168.1.35",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
    },
    "node_3_router": {
        "ip": "192.168.1.1",
        "state": "UP",
        "network_type": "router",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
    },
    "node_4_phone2": {
        "ip": "192.168.1.34",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
    },
    "node_5_phone3": {
        "ip": "192.168.1.36",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
    },
}
