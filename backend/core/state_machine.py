# core/state_machine.py

class IncidentStateMachine:

    allowed_transitions = {
        "OPEN": ["INVESTIGATING"],
        "INVESTIGATING": ["RESOLVED"],
        "RESOLVED": ["CLOSED"]
    }

    def transition(self, incident, new_state, rca=None):

        if new_state == "CLOSED":
            if not rca or not all(rca.values()):
                raise Exception("RCA required before closing")

        if new_state not in self.allowed_transitions.get(incident.status, []):
            raise Exception("Invalid state transition")

        incident.status = new_state

        if new_state == "CLOSED":
            incident.end_time = time.time()
            incident.rca = rca
