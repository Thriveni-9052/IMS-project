# core/models.py

from dataclasses import dataclass, field
from typing import List, Optional
import time

@dataclass
class Incident:
    id: str
    component: str
    severity: str
    status: str = "OPEN"
    signals: List[dict] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    rca: Optional[dict] = None
