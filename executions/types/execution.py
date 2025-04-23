from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateExecutionParams:
    execution_id: int
    status: str
    error_message: Optional[str] = None
