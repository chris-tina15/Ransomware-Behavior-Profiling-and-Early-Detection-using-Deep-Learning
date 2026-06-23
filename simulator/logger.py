import json, time

def log_event(file, source, action, target, value):
    event = {
        "timestamp": time.time(),
        "source": source,
        "action": action,
        "target": target,
        "value": value
    }
    with open(file, "a") as f:
        f.write(json.dumps(event) + "\n")
