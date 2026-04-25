# ============================================================
# export_logs.py
# Network Monitoring & Predictive Failure System
# Phase 1 — Export MongoDB logs to CSV for model training
# ============================================================
# HOW TO RUN:
#   1. Place this file in your project root folder
#   2. Make sure your .env file has MONGO_URI set
#   3. Run: python export_logs.py
#   4. Upload the generated logs.csv to Google Colab
# ============================================================

import os
import pandas as pd
from datetime import datetime

# ── Load environment variables ────────────────────────────
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✅ .env loaded")
except Exception:
    print("⚠️  dotenv not found — make sure MONGO_URI is set in environment")

# ── Connect to MongoDB ────────────────────────────────────
try:
    import pymongo
except ImportError:
    print("❌ pymongo not installed. Run: pip install pymongo dnspython")
    exit(1)

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("❌ MONGO_URI not found in .env file")
    exit(1)

print("🔗 Connecting to MongoDB Atlas...")

try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

# ── Fetch logs ────────────────────────────────────────────
db = client["network_monitor"]
logs_collection = db["logs"]

print("📦 Fetching logs from MongoDB...")

try:
    logs = list(logs_collection.find({}, {"_id": 0}))  # exclude _id field
    print(f"✅ Fetched {len(logs)} log entries")
except Exception as e:
    print(f"❌ Failed to fetch logs: {e}")
    exit(1)

if len(logs) == 0:
    print("⚠️  No logs found in the database. Make sure your monitor has been running.")
    exit(1)

# ── Convert to DataFrame ──────────────────────────────────
print("🔄 Converting to DataFrame...")

df = pd.DataFrame(logs)

# ── Check expected columns ────────────────────────────────
expected_columns = [
    "timestamp",
    "node_name",
    "ip",
    "network_type",
    "state",
    "latency",
    "fails",
]
missing = [col for col in expected_columns if col not in df.columns]

if missing:
    print(f"⚠️  Missing columns: {missing}")
    print(f"   Available columns: {list(df.columns)}")
else:
    print("✅ All expected columns found")

# ── Data Cleaning ─────────────────────────────────────────
print("🧹 Cleaning data...")

# Keep only expected columns (ignore any extras)
df = df[[col for col in expected_columns if col in df.columns]]

# Convert timestamp to datetime if not already
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Drop rows where latency is null (ping failed rows)
before = len(df)
df = df.dropna(subset=["latency"])
after = len(df)
print(f"   Removed {before - after} rows with null latency")

# Convert latency to float (safety)
df["latency"] = df["latency"].astype(float)

# Convert fails to int (safety)
df["fails"] = df["fails"].fillna(0).astype(int)

# Sort by node_name + timestamp (important for feature engineering)
df = df.sort_values(["node_name", "timestamp"]).reset_index(drop=True)

# ── Summary Stats ─────────────────────────────────────────
print("\n📊 Dataset Summary:")
print(f"   Total rows        : {len(df)}")
print(f"   Unique nodes      : {df['node_name'].nunique()}")
print(f"   Date range        : {df['timestamp'].min()} → {df['timestamp'].max()}")
print(f"   Network types     : {df['network_type'].unique().tolist()}")
print(f"\n   State distribution:")
print(df["state"].value_counts().to_string())
print(f"\n   Latency stats (ms):")
print(df["latency"].describe().round(3).to_string())

# ── Save to CSV ───────────────────────────────────────────
OUTPUT_FILE = "logs.csv"

print(f"\n💾 Saving to {OUTPUT_FILE}...")
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Saved {len(df)} rows to {OUTPUT_FILE}")
print(f"\n🎉 Done! Upload '{OUTPUT_FILE}' to Google Colab to begin training.")
print(f"   File location: {os.path.abspath(OUTPUT_FILE)}")
