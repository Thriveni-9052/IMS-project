# services/signal_processor.py

from core.alert_strategy import get_alert_strategy

def process_signal(signal, incident_store, raw_store):

    component = signal["component_id"]
    severity = signal.get("severity", "P3")

    # store raw
    raw_store.append(signal)

    # alert strategy
    strategy = get_alert_strategy(severity)
    strategy.alert(signal)

    # attach to incident
    if component not in incident_store:
        incident_store[component] = {
            "signals": [],
            "status": "OPEN"
        }

    incident_store[component]["signals"].append(signal)
