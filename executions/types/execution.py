from typing import Optional
from dataclasses import dataclass


@dataclass
class UpdateExecutionParams:
    execution_id: int
    status: str
    error_message: Optional[str] = None
