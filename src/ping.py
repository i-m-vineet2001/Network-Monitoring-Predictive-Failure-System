# ping logic
import subprocess

def ping_node(ip: str) -> dict:
    result = subprocess.run(
        ["ping", "-c", "1", ip],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {
            "success": False,
            "latency": None,
            "error": "ping_failed"
        }

    latency = None
    for line in result.stdout.splitlines():
        if "time=" in line:
            time_part = line.split("time=")[1]
            latency = float(time_part.split(" ")[0])
            break

    if latency is None:
        return {
            "success": True,
            "latency": None,
            "error": "latency_parse_failed"
        }

    return {
        "success": True,
        "latency": latency,
        "error": None
    }
