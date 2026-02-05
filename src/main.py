# program entry point
import time
from config import nodes
from monitor import run_monitor

if __name__ == "__main__":
    print("Monitor started")

    while True:
        run_monitor(nodes)
        print("-" * 40)
        time.sleep(5)
