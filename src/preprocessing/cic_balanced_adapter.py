import csv
import json
import random
from pathlib import Path

# ================= CONFIG =================
MAX_REPEAT = 1000
OUT_ROOT = Path("data/processed/sequences")

# ================= FEATURE SELECTION =================
SELECTED_FEATURES = [
    "pslist.nproc",
    "pslist.avg_threads",
    "handles.nhandles",
    "handles.nfile",
    "handles.nkey",
    "dlllist.ndlls",
    "ldrmodules.not_in_load",
    "psxview.not_in_pslist",
    "psxview.not_in_session",
    "malfind.ninjections",
    "malfind.uniqueInjections",
    "svcscan.nservices",
]

# =========================================

def cap(x):
    return int(min(max(x, 0), MAX_REPEAT))

def repeat(token, n):
    return [token] * cap(n)

def row_to_sequence(row):
    seq = []

    # -------- PROCESS --------
    seq += repeat("PROCESS:CREATE", row["pslist.nproc"])

    # -------- FILE / API --------
    files = row["handles.nfile"]
    seq += repeat("API:READ_FILE", files // 2)
    seq += repeat("API:WRITE_FILE", files // 2)

    # -------- REGISTRY --------
    seq += repeat("REGISTRY:SET_KEY", row["handles.nkey"])

    # -------- RESOURCE / MEMORY --------
    seq += repeat("RESOURCE:CPU_MEM", row["malfind.ninjections"])
    seq += repeat("RESOURCE:CPU_MEM", row["callbacks.ncallbacks"])

    # -------- NETWORK --------
    seq += repeat("NETWORK:CONNECT", row["handles.nport"])

    # Reduce ordering bias
    random.shuffle(seq)

    return seq

def extract_features(row):
    """
    Keep original CIC-MalMem numeric features
    """
    return {k: float(row.get(k, 0.0)) for k in SELECTED_FEATURES}

def convert_csv(csv_path, label):
    out_dir = OUT_ROOT / label
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            numeric = {k: float(v) for k, v in row.items() if k != "Filename"}

            seq = row_to_sequence(numeric)
            features = extract_features(numeric)

            out = {
                "label": label,
                "sequence": seq,
                "features": features
            }

            with open(out_dir / f"sample_{i}.json", "w") as out_f:
                json.dump(out, out_f, indent=2)

    print(f"✅ Converted {csv_path} → {label}")

# ================= MAIN =================
if __name__ == "__main__":
    # RANSOMWARE CSVs
    convert_csv("data/cic/output1.csv", "ransomware")
    convert_csv("data/cic/output2.csv", "ransomware")

    # BENIGN CSVs
    convert_csv("data/cic/output3.csv", "benign")
