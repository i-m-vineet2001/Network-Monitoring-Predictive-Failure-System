# src/network_profiles.py
#
# Each profile describes how a simulated network BEHAVES.
# The SimNode uses these values to generate realistic fake ping results.
#
# latency_base   – normal latency in ms (mean)
# latency_jitter – random ± variation added each cycle (std dev)
# spike_prob     – probability (0-1) of a random latency spike this cycle
# spike_range    – (min, max) ms added during a spike
# drop_prob      – probability (0-1) that a single ping is lost (no reply)
# fail_prob      – probability (0-1) that the node goes into a sustained failure
#                  (stays down for fail_duration_range cycles before recovering)
# fail_duration  – (min, max) number of cycles a sustained failure lasts
# description    – human readable label shown in GUI

NETWORK_PROFILES = {
    # ── Real home network (your router / laptop / phone) ─────────────
    "home": {
        "latency_base": 5,
        "latency_jitter": 2,
        "spike_prob": 0.03,
        "spike_range": (30, 80),
        "drop_prob": 0.01,
        "fail_prob": 0.002,
        "fail_duration": (2, 5),
        "description": "Home WiFi",
    },
    # ── Simulated office LAN ──────────────────────────────────────────
    # Medium latency, very stable, rare drops
    "office": {
        "latency_base": 25,
        "latency_jitter": 8,
        "spike_prob": 0.05,
        "spike_range": (50, 120),
        "drop_prob": 0.02,
        "fail_prob": 0.005,
        "fail_duration": (2, 6),
        "description": "Office LAN",
    },
    # ── Simulated mobile / 4G network ────────────────────────────────
    # High latency, noisy, occasional drops
    "mobile": {
        "latency_base": 80,
        "latency_jitter": 30,
        "spike_prob": 0.15,
        "spike_range": (150, 400),
        "drop_prob": 0.08,
        "fail_prob": 0.02,
        "fail_duration": (3, 10),
        "description": "Mobile / 4G",
    },
    # ── Simulated cloud / remote server ──────────────────────────────
    # Higher base latency, variable, rare but longer failures
    "cloud": {
        "latency_base": 120,
        "latency_jitter": 40,
        "spike_prob": 0.08,
        "spike_range": (200, 500),
        "drop_prob": 0.03,
        "fail_prob": 0.008,
        "fail_duration": (4, 15),
        "description": "Cloud / Remote",
    },
    # ── Simulated unstable / flaky network ───────────────────────────
    # Frequent spikes, high drop rate, goes down often
    "unstable": {
        "latency_base": 60,
        "latency_jitter": 50,
        "spike_prob": 0.30,
        "spike_range": (200, 800),
        "drop_prob": 0.20,
        "fail_prob": 0.05,
        "fail_duration": (3, 12),
        "description": "Unstable / Flaky",
    },
}
