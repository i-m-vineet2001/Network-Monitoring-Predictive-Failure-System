

from db.mongo import logs_collection
from datetime import datetime, timedelta


def get_logs_by_range(range_type: str = "all") -> list:
    """
    Fetch logs from MongoDB filtered by time range.
    range_type: "all" | "day" | "week" | "month"
    """
    if logs_collection is None:
        return []

    query = {}
    now = datetime.now()

    if range_type == "day":
        query["timestamp"] = {"$gte": now - timedelta(days=1)}
    elif range_type == "week":
        query["timestamp"] = {"$gte": now - timedelta(weeks=1)}
    elif range_type == "month":
        query["timestamp"] = {"$gte": now - timedelta(days=30)}

    try:
        return list(logs_collection.find(query).sort("timestamp", -1).limit(200))
    except Exception as exc:
        print(f"[ERROR] get_logs_by_range: {exc}")
        return []


def insert_log(node_name, ip, network_type, state, latency, fails):
    if logs_collection is None:
        return

    try:
        logs_collection.insert_one(
            {
                "timestamp": datetime.now(),
                "node_name": node_name,
                "ip": ip,
                "network_type": network_type,
                "state": state,
                "latency": latency,
                "fails": fails,
            }
        )
    except Exception as exc:
        print(f"[ERROR] insert_log for {node_name}: {str(exc)[:100]}")