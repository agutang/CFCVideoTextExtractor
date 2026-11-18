class EventDetector:
    """Rising edges are immediate; absence stabilization only delays rearming."""
    def __init__(self, absence=0.0):
        self.absence = absence
        self.present = False
        self.missing_since = None

    def update(self, detected, timestamp):
        if detected:
            self.missing_since = None
            if not self.present:
                self.present = True
                return True
        elif self.present:
            if self.missing_since is None:
                self.missing_since = timestamp
            if timestamp - self.missing_since + 1e-9 >= self.absence:
                self.present = False
                self.missing_since = None
        return False
