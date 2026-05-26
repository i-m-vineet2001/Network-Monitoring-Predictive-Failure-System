

# src/sim_node.py
#
# A SimNode pretends to be a real device on a network.
# Every HEARTBEAT_INTERVAL seconds it generates a realistic
# ping result (latency, packet_loss, jitter) based on its
# network profile, then sends it as JSON to the Controller
# via a plain TCP socket.
#
# Usage (run directly for testing):
#   python src/sim_node.py --node node_office_a --host 127.0.0.1 --port 9000
#
# Normally started automatically by main.py as daemon threads.

import os
import sys
import json
import random
import socket
import time
import threading
import argparse
from datetime import datetime

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from network_profiles import NETWORK_PROFILES

HEARTBEAT_INTERVAL = 5  # seconds — same cadence as the real ping monitor
RECONNECT_DELAY = 3  # seconds — wait before retrying lost connection


class SimNode:
    """
    Simulates one network node.

    State machine (mirrors the real monitor):
      UP        – normal operation
      DEGRADED  – latency above threshold
      DOWN      – in a sustained failure window

    The node generates its own 'ping result' using the
    network profile probabilities, then reports it to
    the Controller over a socket connection.
    """

    LATENCY_THRESHOLD = 30  # ms — matches monitor.py

    def __init__(
        self,
        node_name: str,
        node_config: dict,
        controller_host: str = "127.0.0.1",
        controller_port: int = 9000,
    ):
        self.name = node_name
        self.config = node_config  # from config.py nodes dict
        self.host = controller_host
        self.port = controller_port

        profile_key = node_config.get("network_profile", "home")
        self.profile = NETWORK_PROFILES.get(profile_key, NETWORK_PROFILES["home"])

        # Internal state
        self._state = "UP"
        self._fail_count = 0
        self._down_cycles = 0  # how many more cycles to stay DOWN
        self._latency_history = []
        self._running = False
        self._lock = threading.Lock()

    # ── Simulation helpers ────────────────────────────────────────────

    def _generate_ping_result(self) -> dict:
        """
        Generate a realistic fake ping result using the network profile.
        Returns the same dict format as the real ping_node() function:
          { success: bool, latency: float|None, loss: float, jitter: float }
        """
        p = self.profile

        # If currently in a sustained DOWN window, keep failing
        if self._down_cycles > 0:
            self._down_cycles -= 1
            return {"success": False, "latency": None, "loss": 1.0, "jitter": 0.0}

        # Randomly enter a new sustained failure
        if random.random() < p["fail_prob"]:
            duration = random.randint(*p["fail_duration"])
            self._down_cycles = duration
            return {"success": False, "latency": None, "loss": 1.0, "jitter": 0.0}

        # Single packet drop (no sustained failure)
        if random.random() < p["drop_prob"]:
            return {"success": False, "latency": None, "loss": 1.0, "jitter": 0.0}

        # Normal ping — calculate latency
        base = p["latency_base"]
        jitter = random.gauss(0, p["latency_jitter"])
        latency = max(0.1, base + jitter)

        # Random latency spike
        if random.random() < p["spike_prob"]:
            latency += random.uniform(*p["spike_range"])

        # Packet loss ratio (partial — single ping is either 0% or 100%)
        loss = 0.0

        # Jitter = variation from last reading
        if self._latency_history:
            jitter_val = abs(latency - self._latency_history[-1])
        else:
            jitter_val = abs(jitter)

        self._latency_history.append(latency)
        if len(self._latency_history) > 30:
            self._latency_history.pop(0)

        return {
            "success": True,
            "latency": round(latency, 3),
            "loss": round(loss, 3),
            "jitter": round(jitter_val, 3),
        }

    def _evaluate_state(self, result: dict) -> str:
        """Mirror of monitor.py evaluate_status() — same logic."""
        if not result["success"]:
            self._fail_count += 1
            threshold = 8 if self.config.get("ping_blocked") else 3
            if self._state == "DOWN":
                return "DOWN"
            return "DOWN" if self._fail_count >= threshold else self._state
        else:
            self._fail_count = 0
            lat = result.get("latency")
            if lat is None:
                return "UP"
            return "DEGRADED" if lat > self.LATENCY_THRESHOLD else "UP"

    # Maps network_profile name → predictor-safe network_type
    # Predictor net_map only knows: wifi=0, router=1, ethernet=2
    _PROFILE_TO_NET_TYPE = {
        "home": "wifi",
        "office": "ethernet",
        "mobile": "wifi",  # closest match — mobile not in predictor net_map
        "cloud": "wifi",  # closest match — cloud not in predictor net_map
        "unstable": "wifi",
    }

    def _build_heartbeat(self, result: dict) -> dict:
        """Build the JSON payload sent to the Controller."""
        profile = self.config.get("network_profile", "home")
        net_type = self._PROFILE_TO_NET_TYPE.get(profile, "wifi")
        return {
            "node": self.name,
            "ip": self.config["ip"],
            "network": profile,
            "network_label": self.profile["description"],
            "network_type": net_type,  # predictor-safe type (wifi/ethernet/router)
            "state": self._state,
            "latency": result.get("latency"),
            "loss": result.get("loss", 0.0),
            "jitter": result.get("jitter", 0.0),
            "fail_count": self._fail_count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "simulated": True,
        }

    # ── Socket communication ──────────────────────────────────────────

    def _send(self, sock: socket.socket, payload: dict):
        """Send a newline-delimited JSON message."""
        msg = json.dumps(payload) + "\n"
        sock.sendall(msg.encode("utf-8"))

    def _connect(self) -> socket.socket:
        """Keep retrying until the Controller is available."""
        while self._running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.host, self.port))
                s.settimeout(None)
                print(f"[{self.name}] Connected to controller {self.host}:{self.port}")
                return s
            except (ConnectionRefusedError, OSError):
                print(
                    f"[{self.name}] Controller not ready, retrying in {RECONNECT_DELAY}s..."
                )
                time.sleep(RECONNECT_DELAY)
        return None

    # ── Main loop ─────────────────────────────────────────────────────

    def run(self):
        """Main heartbeat loop — runs in its own daemon thread."""
        self._running = True
        sock = None

        while self._running:
            # Connect / reconnect
            if sock is None:
                sock = self._connect()
                if sock is None:
                    break

            try:
                result = self._generate_ping_result()
                self._state = self._evaluate_state(result)
                heartbeat = self._build_heartbeat(result)

                self._send(sock, heartbeat)

                print(
                    f"[{self.name}] {self._state:8s} | "
                    f"lat={str(result.get('latency', 'None')):>8}ms | "
                    f"loss={result.get('loss', 0):.0%} | "
                    f"jitter={result.get('jitter', 0):.1f}ms | "
                    f"net={self.profile['description']}"
                )

            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                print(f"[{self.name}] Connection lost ({e}), reconnecting...")
                try:
                    sock.close()
                except Exception:
                    pass
                sock = None
                continue

            time.sleep(HEARTBEAT_INTERVAL)

        if sock:
            try:
                sock.close()
            except Exception:
                pass

    def stop(self):
        self._running = False

    def start_thread(self) -> threading.Thread:
        """Start this node in a background daemon thread."""
        t = threading.Thread(target=self.run, name=f"SimNode-{self.name}", daemon=True)
        t.start()
        return t


# ── CLI entry point (for testing a single node standalone) ───────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a single simulated node")
    parser.add_argument("--node", default="test_node", help="Node name")
    parser.add_argument("--profile", default="mobile", help="Network profile name")
    parser.add_argument("--ip", default="10.0.0.99", help="Simulated IP")
    parser.add_argument("--host", default="127.0.0.1", help="Controller host")
    parser.add_argument("--port", type=int, default=9000, help="Controller port")
    args = parser.parse_args()

    config = {
        "ip": args.ip,
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "network_profile": args.profile,
    }
    node = SimNode(args.node, config, args.host, args.port)
    print(f"Starting simulated node '{args.node}' with profile '{args.profile}'")
    print("Press Ctrl+C to stop.\n")
    try:
        node.run()
    except KeyboardInterrupt:
        node.stop()
        print("\nStopped.")