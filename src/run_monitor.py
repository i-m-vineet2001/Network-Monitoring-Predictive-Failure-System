#!/usr/bin/env python3
# run_monitor.py — run the monitor loop in foreground (no GUI)
import time
import sys
import os

# ensure project src is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor import run_monitor
from config import nodes


def main():
    print("Starting monitor loop (foreground). Ctrl+C to stop.")
    try:
        while True:
            run_monitor(nodes)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Monitor stopped")


if __name__ == "__main__":
    main()
