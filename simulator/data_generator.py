import json
import random
import time
from pathlib import Path

# ================= CONFIG =================
OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EVENTS_PER_BEHAVIOR = 30000     # 🔥 SCALE HERE
START_TIME = time.time()

# ==========================================

def save_json(filename, data):
    with open(OUTPUT_DIR / filename, "w") as f:
        json.dump(data, f, indent=2)

def ts(offset):
    return START_TIME + offset

# ---------- PROCESS BEHAVIOR ----------
def generate_process_events(label):
    events = []
    for i in range(EVENTS_PER_BEHAVIOR):
        if label == "ransomware":
            process = random.choice(["encryptor.exe", "locker.exe", "helper.exe"])
        else:
            process = random.choice(["chrome.exe", "word.exe", "explorer.exe"])

        events.append({
            "timestamp": ts(i * 0.01),
            "source": "PROCESS",
            "action": "CREATE",
            "process_name": process,
            "pid": random.randint(1000, 9000),
            "label": label
        })
    return events

# ---------- API / SYSTEM CALLS ----------
def generate_api_events(label):
    events = []
    for i in range(EVENTS_PER_BEHAVIOR):
        if label == "ransomware":
            action = random.choice(["READ_FILE", "WRITE_FILE", "RENAME_FILE", "CRYPT_ENCRYPT"])
        else:
            action = random.choice(["READ_FILE", "OPEN_FILE", "CLOSE_FILE"])

        events.append({
            "timestamp": ts(i * 0.015),
            "source": "API",
            "action": action,
            "file": f"file_{random.randint(1,5000)}.txt",
            "label": label
        })
    return events

# ---------- REGISTRY ----------
def generate_registry_events(label):
    events = []
    for i in range(EVENTS_PER_BEHAVIOR):
        if label == "ransomware":
            key = random.choice([
                "HKCU\\Software\\Microsoft\\Windows\\Run",
                "HKLM\\System\\Services",
                "HKCU\\ControlPanel"
            ])
            action = "SET_KEY"
        else:
            key = "HKCU\\Software\\Application"
            action = "READ_KEY"

        events.append({
            "timestamp": ts(i * 0.02),
            "source": "REGISTRY",
            "action": action,
            "key": key,
            "label": label
        })
    return events

# ---------- RESOURCE UTILIZATION ----------
def generate_resource_events(label):
    events = []
    for i in range(EVENTS_PER_BEHAVIOR):
        if label == "ransomware":
            cpu = random.randint(70, 98)
            mem = random.randint(1500, 3200)
        else:
            cpu = random.randint(5, 35)
            mem = random.randint(200, 700)

        events.append({
            "timestamp": ts(i * 0.01),
            "source": "RESOURCE",
            "action": "CPU_MEM",
            "cpu": cpu,
            "memory_mb": mem,
            "label": label
        })
    return events

# ---------- NETWORK ----------
def generate_network_events(label):
    events = []
    for i in range(EVENTS_PER_BEHAVIOR):
        if label == "ransomware":
            ip = f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            action = "CONNECT"
        else:
            ip = random.choice(["8.8.8.8", "1.1.1.1"])
            action = "DNS_QUERY"

        events.append({
            "timestamp": ts(i * 0.03),
            "source": "NETWORK",
            "action": action,
            "destination": ip,
            "bytes": random.randint(500, 5000),
            "label": label
        })
    return events

# ================= MAIN =================
if __name__ == "__main__":
    print("Generating synthetic ransomware & benign datasets...")

    save_json("process_benign.json", generate_process_events("benign"))
    save_json("process_ransomware.json", generate_process_events("ransomware"))

    save_json("api_benign.json", generate_api_events("benign"))
    save_json("api_ransomware.json", generate_api_events("ransomware"))

    save_json("registry_benign.json", generate_registry_events("benign"))
    save_json("registry_ransomware.json", generate_registry_events("ransomware"))

    save_json("resource_benign.json", generate_resource_events("benign"))
    save_json("resource_ransomware.json", generate_resource_events("ransomware"))

    save_json("network_benign.json", generate_network_events("benign"))
    save_json("network_ransomware.json", generate_network_events("ransomware"))

    print("✅ Dataset generation complete.")
