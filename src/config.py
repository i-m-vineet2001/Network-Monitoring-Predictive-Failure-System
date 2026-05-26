
# src/config.py
#
# Node definitions for BOTH real nodes (pinged directly) and
# simulated nodes (connected via SimNode socket to the Controller).
#
# Real nodes  → used by monitor.py → ping_node() called directly
# Sim nodes   → used by sim_node.py → send heartbeat to controller
#
# The extra fields (network_profile, simulated) are ignored by
# the real monitor — they are only read by SimNode.

LATENCY_THRESHOLD = 30  # ms — >30ms = DEGRADED

# ── REAL nodes (your actual home network devices) ─────────────────────


real_nodes = {
    "node_1_phone1": {
        "ip": "192.168.1.33",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": True,  # iPhone silently drops ICMP — needs higher fail threshold
        "last_ml_alert": None,  # Track last ML alert level to avoid spam
        "simulated": False,
    },
    "node_2_laptop": {
        "ip": "192.168.1.35",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
        "simulated": False,
    },
    "node_3_router": {
        "ip": "192.168.1.1",
        "state": "UP",
        "network_type": "router",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
        "simulated": False,
    },
    "node_4_phone2": {
        "ip": "192.168.1.34",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
        "simulated": False,
    },
    "node_5_phone3": {
        "ip": "192.168.1.36",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
        "simulated": False,
    },
}


# ── SIMULATED nodes (fake devices on different virtual networks) ───────
#
# Network 2: Office LAN (10.0.0.x)
# Network 3: Mobile / 4G (172.16.0.x)
# Network 4: Cloud / Remote server (203.0.113.x — TEST-NET-3, never routable)
# Network 5: Unstable / flaky (192.168.2.x)
#
# IPs are illustrative labels — not actually pinged.

sim_nodes = {
    # ── Office LAN ────────────────────────────────────────────────
    "node_office_a": {
        "ip": "10.0.0.2",
        "state": "UP",
        "network_type": "ethernet",
        "network_profile": "office",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "simulated": True,
    },
    "node_office_b": {
        "ip": "10.0.0.3",
        "state": "UP",
        "network_type": "ethernet",
        "network_profile": "office",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "simulated": True,
    },
    "node_office_router": {
        "ip": "10.0.0.1",
        "state": "UP",
        "network_type": "router",
        "network_profile": "office",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "simulated": True,
    },
    # ── Mobile / 4G ───────────────────────────────────────────────
    "node_mobile_a": {
        "ip": "172.16.0.2",
        "state": "UP",
        "network_type": "wifi",  # mapped from mobile — predictor net_map uses wifi
        "network_profile": "mobile",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": True,  # mobile devices often block ICMP too
        "simulated": True,
    },
    "node_mobile_b": {
        "ip": "172.16.0.3",
        "state": "UP",
        "network_type": "wifi",  # mapped from mobile — predictor net_map uses wifi
        "network_profile": "mobile",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": True,
        "simulated": True,
    },
    # ── Cloud / Remote servers ────────────────────────────────────
    "node_cloud_server_a": {
        "ip": "203.0.113.10",
        "state": "UP",
        "network_type": "wifi",  # mapped from cloud — predictor net_map uses wifi
        "network_profile": "cloud",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "simulated": True,
    },
    "node_cloud_server_b": {
        "ip": "203.0.113.11",
        "state": "UP",
        "network_type": "wifi",  # mapped from cloud — predictor net_map uses wifi
        "network_profile": "cloud",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "simulated": True,
    },
    # ── Unstable / flaky network ──────────────────────────────────
    "node_unstable_a": {
        "ip": "192.168.2.2",
        "state": "UP",
        "network_type": "wifi",
        "network_profile": "unstable",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "simulated": True,
    },
    "node_unstable_b": {
        "ip": "192.168.2.3",
        "state": "UP",
        "network_type": "wifi",
        "network_profile": "unstable",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "simulated": True,
    },
}

# ── Combined dict used by the real ping monitor ────────────────────────
# (only real_nodes — sim_nodes go through SimNode + Controller)
nodes = real_nodes

# ── All nodes combined — used by GUI to display everything ────────────
all_nodes = {**real_nodes, **sim_nodes}