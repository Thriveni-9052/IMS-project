# core/alert_strategy.py

class AlertStrategy:
    def alert(self, signal):
        pass


class P0Alert(AlertStrategy):
    def alert(self, signal):
        print("🔥 P0 ALERT: Critical System Failure")


class P1Alert(AlertStrategy):
    def alert(self, signal):
        print("⚠️ P1 ALERT: Queue Issue")


class P2Alert(AlertStrategy):
    def alert(self, signal):
        print("⚡ P2 ALERT: Cache Issue")


def get_alert_strategy(severity):
    if severity == "P0":
        return P0Alert()
    elif severity == "P1":
        return P1Alert()
    return P2Alert()

