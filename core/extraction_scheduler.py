from collections import deque
from dataclasses import dataclass

@dataclass
class Event:
    id: int
    occurred: float
    target: float
    status: str = 'pending'

class Scheduler:
    def __init__(self, delay):
        self.delay = delay
        self.pending = deque()
        self.count = 0

    def add(self, timestamp):
        self.count += 1
        event = Event(self.count, timestamp, timestamp + self.delay)
        self.pending.append(event)
        return event

    def due(self, timestamp):
        while self.pending and self.pending[0].target <= timestamp + 1e-9:
            yield self.pending.popleft()
