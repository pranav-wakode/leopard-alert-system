from pydantic import BaseModel
from typing import Optional

class DetectionResponse(BaseModel):
    detected: bool
    confidence: Optional[float] = None

class AlertResponse(BaseModel):
    alert: bool

class LogEntry(BaseModel):
    timestamp: str
    detected: bool
    confidence: Optional[float] = None