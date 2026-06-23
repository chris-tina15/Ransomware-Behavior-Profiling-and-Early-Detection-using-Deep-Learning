import time
import random
from simulator.logger import log_event

def run_ransomware():
    for i in range(50):
        log_event("data/raw/process.json", "PROCESS", "CREATE", f"pid_{i}", 1)
        log_event("data/raw/api.json", "API", "WRITE_FILE", f"file_{i}", random.randint(1000, 5000))
        log_event("data/raw/registry.json", "REGISTRY", "SET_KEY", "HKCU\\Run", 1)
        log_event("data/raw/resource.json", "RESOURCE", "CPU_MEM", "system", random.uniform(70, 95))
        log_event("data/raw/network.json", "NETWORK", "CONNECT", "10.0.0.5", 2048)
        time.sleep(0.01)
