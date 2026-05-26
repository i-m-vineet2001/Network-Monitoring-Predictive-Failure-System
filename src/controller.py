








import errno
import os
import sys
import json
import socket
import threading
from collections import deque
from datetime import datetime

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

MODEL_DIR = os.path.join(ROOT_DIR, "model")
sys.path.insert(0, MODEL_DIR)

_predictor_available = False
try:
    from predictor import predict_node_failure_from_buffer

    _predictor_available = True
    print("[Controller] ✅ ML predictor loaded")
except Exception as e:
    print(f"[Controller] ⚠️ ML predictor not available: {e}")

    def predict_node_failure_from_buffer(*args, **kwargs):
        return {
            "failure_probability": 0.0,
            "prediction": 0,
            "risk_level": "LOW",
            "alert": "N/A",
            "enough_data": False,
        }


from db.file_log_service import write_log_file
from db.log_service import insert_log

CONTROLLER_HOST = "127.0.0.1"
CONTROLLER_PORT = 9000
BUFFER_SIZE = 4096
HISTORY_WINDOW = 10
_history: dict = {}


def _get_history(node_name: str) -> deque:
    if node_name not in _history:
        _history[node_name] = deque(maxlen=HISTORY_WINDOW)
    return _history[node_name]


def _handle_client(conn: socket.socket, addr: tuple):
    """
    Handle one connected SimNode.
    Each SimNode holds a persistent connection and sends
    newline-delimited JSON heartbeats every 5 seconds.
    """
    print(f"[Controller] New connection from {addr}")
    buffer = ""

    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            buffer += data.decode("utf-8", errors="replace")

            # Process all complete newline-delimited messages
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                    _process_heartbeat(msg)
                except json.JSONDecodeError as e:
                    print(f"[Controller] Bad JSON from {addr}: {e}")

    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        conn.close()
        print(f"[Controller] Connection closed: {addr}")


def _process_heartbeat(msg: dict):
    """
    Process one heartbeat message from a SimNode.
    Updates the shared node state and writes to logs.
    """
    node_name = msg.get("node", "unknown")
    ip = msg.get("ip", "0.0.0.0")
    network = msg.get("network", "home")  # profile name (e.g. 'mobile')
    net_label = msg.get("network_label", network)
    # network_type is the predictor-safe value sent by sim_node (wifi/ethernet/router)
    net_type = msg.get("network_type", "wifi")
    state = msg.get("state", "UNKNOWN")
    latency = msg.get("latency")
    loss = msg.get("loss", 0.0)
    jitter = msg.get("jitter", 0.0)
    fail_count = msg.get("fail_count", 0)
    timestamp = msg.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # ML prediction for simulated heartbeat data
    hist = _get_history(node_name)
    hist.append(
        {
            "timestamp": timestamp,
            "latency": latency,
            "fails": fail_count,
            "state": state,
        }
    )

    ml = predict_node_failure_from_buffer(
        node_name=node_name,
        buffer=list(hist),
        network_type=net_type,  # predictor-safe: wifi/ethernet/router
    )
    ml_prob = ml.get("failure_probability", 0.0)

    # Terminal output
    lat_str = f"{latency:.1f}" if latency is not None else "None"
    print(
        f"[{timestamp}] {node_name:20s} [{net_label:15s}] → {state:8s} "
        f"| lat={lat_str:>7}ms | loss={loss:.0%} | jitter={jitter:.1f}ms "
        f"| fails={fail_count} | ml={ml_prob:.2f}"
    )

    # Write to log.txt (same format as the real monitor — GUI reads this)
    try:
        write_log_file(node_name, ip, network, state, latency, fail_count, ml_prob)
    except TypeError:
        # Old file_log_service doesn't accept ml_prob — try without it
        try:
            write_log_file(node_name, ip, network, state, latency, fail_count)
        except Exception as exc2:
            # Last resort: write manually so sim node data is never lost
            from datetime import datetime as _dt

            ts = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
            import os as _os

            log = _os.path.join(ROOT_DIR, "logs", "log.txt")
            _os.makedirs(_os.path.dirname(log), exist_ok=True)
            with open(log, "a") as _f:
                _f.write(
                    f"{ts} | {node_name} | {ip} | {state} | "
                    f"type={network} | latency={latency} | fails={fail_count} | ml={ml_prob}\n"
                )
    except Exception as exc:
        print(f"[Controller] file_log_service error: {exc}")

    # Write to MongoDB
    try:
        insert_log(node_name, ip, network, state, latency, fail_count)
    except Exception as exc:
        print(f"[Controller] MongoDB error: {exc}")


def run_controller(host: str = CONTROLLER_HOST, port: int = CONTROLLER_PORT):
    """
    Start the TCP server and accept SimNode connections forever.
    Runs in the main controller thread; each client gets its own thread.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((host, port))
    except OSError as exc:
        if exc.errno == errno.EADDRINUSE:
            print(
                f"[Controller] Port {port} is already in use. "
                "If another controller is already running, the application will use it."
            )
            server.close()
            return
        raise

    server.listen(20)  # up to 20 simultaneous node connections
    print(f"[Controller] Listening on {host}:{port}")

    while True:
        try:
            conn, addr = server.accept()
            t = threading.Thread(
                target=_handle_client,
                args=(conn, addr),
                daemon=True,
                name=f"Client-{addr[1]}",
            )
            t.start()
        except OSError:
            break

    server.close()


def start_controller_thread(
    host: str = CONTROLLER_HOST, port: int = CONTROLLER_PORT
) -> threading.Thread:
    """Start the controller in a background daemon thread."""
    t = threading.Thread(
        target=run_controller, args=(host, port), daemon=True, name="Controller"
    )
    t.start()
    return t


if __name__ == "__main__":
    print("Starting Central Controller (standalone mode)...")
    print("Waiting for SimNode connections on port 9000")
    print("Press Ctrl+C to stop.\n")
    try:
        run_controller()
    except KeyboardInterrupt:
        print("\nController stopped.")