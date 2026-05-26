import time
import threading
import sys
import os

# ── ROOT is one level above src/ ──
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Make both src/ and root visible to Python
sys.path.insert(0, ROOT_DIR)  # → gives access to gui/
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT_DIR, ".env"))  # load .env from root

from config import nodes, sim_nodes
from monitor import run_monitor
from controller import start_controller_thread
from sim_node import SimNode
from gui.login_window import LoginWindow
from gui.theme import DARK_THEME

from PySide6.QtWidgets import QApplication


def monitor_loop():
    while True:
        run_monitor(nodes)
        time.sleep(5)


if __name__ == "__main__":
    print("🚀 Starting Network Monitor...")

    # ── Start Controller (listens for SimNode heartbeats) ───────────────
    print("[Main] Starting Controller server...")
    controller_thread = start_controller_thread("127.0.0.1", 9000)
    time.sleep(1)  # give controller time to bind

    # ── Start SimNode clients (send heartbeats to Controller) ──────────
    print("[Main] Starting simulated nodes...")
    sim_threads = []
    for node_name, node_config in sim_nodes.items():
        sim_node = SimNode(
            node_name=node_name,
            node_config=node_config,
            controller_host="127.0.0.1",
            controller_port=9000,
        )
        t = sim_node.start_thread()
        sim_threads.append(t)
        print(f"[Main]   → {node_name} started")

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    login_window = LoginWindow()
    login_window.show()

    # ── Start real monitor (pings real_nodes) ──────────────────────────
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    sys.exit(app.exec())
