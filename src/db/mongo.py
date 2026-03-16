


import os
import sys

# ── load .env from project root ──
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(ROOT_DIR, ".env"))
except Exception:
    pass

try:
    import pymongo
except ImportError:
    pymongo = None

client = None
db = None
logs_collection = None
users_collection = None

if pymongo is None:
    print("[DB] pymongo not installed — MongoDB disabled")
else:
    mongo_uri = os.getenv("MONGO_URI")
    try:
        if not mongo_uri:
            raise ValueError("MONGO_URI missing in .env")

        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")

        db = client["network_monitor"]
        logs_collection = db["logs"]
        users_collection = db["users"]

        print("✅ MongoDB connected")

    except Exception as exc:
        print(f"❌ MongoDB unavailable: {exc}")