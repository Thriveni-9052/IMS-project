import time

incidents = []
component_last_time = {}

def get_open_incident(component):
    for inc in incidents:
        if inc["component"] == component and inc["status"] != "CLOSED":
            return inc
    return None


def create_incident(signal):
    inc = {
        "id": f"INC{len(incidents)+1:03d}",
        "component": signal["component_id"],
        "severity": signal.get("severity", "P3"),
        "status": "OPEN",
        "signals": [signal],
        "start_time": time.time()
    }
    incidents.append(inc)
    return inc


def process_signal(signal):
    comp = signal["component_id"]
    now = time.time()

    # reuse existing incident
    incident = get_open_incident(comp)
    if incident:
        incident["signals"].append(signal)
        return incident["id"]

    # debounce check (10 sec)
    last_time = component_last_time.get(comp)

    if last_time and (now - last_time < 10):
        incident = get_open_incident(comp)
        if incident:
            incident["signals"].append(signal)
            return incident["id"]

    # create new incident
    component_last_time[comp] = now
    new_inc = create_incident(signal)
    return new_inc["id"]
