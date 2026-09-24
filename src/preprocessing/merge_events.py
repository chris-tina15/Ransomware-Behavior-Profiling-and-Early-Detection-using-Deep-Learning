import json
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "process_benign.json",
    "process_ransomware.json",
    "api_benign.json",
    "api_ransomware.json",
    "registry_benign.json",
    "registry_ransomware.json",
    "resource_benign.json",
    "resource_ransomware.json",
    "network_benign.json",
    "network_ransomware.json",
]

def load_events(filename):
    with open(RAW_DIR / filename, "r") as f:
        return json.load(f)

def normalize_event(event):
    return {
        "timestamp": event["timestamp"],
        "source": event["source"],
        "action": event["action"],
        "label": event["label"]
    }

def merge():
    ransomware_events = []
    benign_events = []

    for file in FILES:
        events = load_events(file)
        for e in events:
            norm = normalize_event(e)
            if norm["label"] == "ransomware":
                ransomware_events.append(norm)
            else:
                benign_events.append(norm)

    # 🔑 Temporal ordering
    ransomware_events.sort(key=lambda x: x["timestamp"])
    benign_events.sort(key=lambda x: x["timestamp"])

    with open(OUT_DIR / "unified_sequence_ransomware.json", "w") as f:
        json.dump(ransomware_events, f, indent=2)

    with open(OUT_DIR / "unified_sequence_benign.json", "w") as f:
        json.dump(benign_events, f, indent=2)

    print(f"✅ Ransomware events: {len(ransomware_events)}")
    print(f"✅ Benign events    : {len(benign_events)}")

if __name__ == "__main__":
    merge()
