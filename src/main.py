
import time
import threading
import sys
import os

# ── ROOT is one level above src/ ──
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Make both src/ and root visible to Python
sys.path.insert(0, ROOT_DIR)  # → gives access to gui/
sys.path.insert(
    0, os.path.join(ROOT_DIR, "src")
)  # → gives access to db/, config, monitor

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT_DIR, ".env"))  # load .env from root

from config import nodes
from monitor import run_monitor
from gui.login_window import LoginWindow
from gui.theme import DARK_THEME

from PySide6.QtWidgets import QApplication


def monitor_loop():
    while True:
        run_monitor(nodes)
        time.sleep(5)


if __name__ == "__main__":
    print("🚀 Starting Network Monitor...")

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    login_window = LoginWindow()
    login_window.show()

    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    sys.exit(app.exec())