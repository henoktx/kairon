from typing import List, Optional
from dataclasses import dataclass


@dataclass
class EmailParams:
    to_email: List[str]
    subject: str
    content: str
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    cc: Optional[List[str]] = None
