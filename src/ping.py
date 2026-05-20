# src/ping.py
import subprocess
import platform
import re


def ping_node(ip: str, ping_blocked: bool = False) -> dict:
    if ping_blocked:
        # For devices that don't respond to ping, simulate success with no latency
        return {"success": True, "latency": None, "error": "ping_blocked"}

    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", "1000", ip]  # -w in ms on Windows
    elif system == "darwin":
        # macOS: -W is in MILLISECONDS (not seconds like Linux!)
        # -W 2000 = 2 second timeout → correct
        cmd = ["ping", "-c", "1", "-W", "2000", ip]
    else:
        # Linux: -W is in SECONDS
        cmd = ["ping", "-c", "1", "-W", "2", ip]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            match = re.search(r"time[=<](\d+\.?\d*)\s*ms", result.stdout, re.IGNORECASE)
            latency = float(match.group(1)) if match else None
            if latency is None:
                print(
                    f"[WARN] Ping ok for {ip} but latency not parsed. stdout: {result.stdout!r}"
                )
            return {"success": True, "latency": latency, "error": None}

        return {"success": False, "latency": None, "error": "ping_failed"}

    except subprocess.TimeoutExpired:
        return {"success": False, "latency": None, "error": "timeout"}
    except Exception as e:
        return {"success": False, "latency": None, "error": str(e)}
