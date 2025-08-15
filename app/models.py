from pydantic import BaseModel, HttpUrl
from typing import Optional


class TargetCreate(BaseModel):
url: HttpUrl
interval_seconds: int = 60
enabled: bool = True


class Target(TargetCreate):
id: int


class CheckResult(BaseModel):
id: int
target_id: int
ts_utc: str
status_code: Optional[int]
latency_ms: Optional[float]
ok: bool
error: Optional[str] = None