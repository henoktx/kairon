from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmailParams:
    to_email: List[str]
    subject: str
    content: str
    html_content: Optional[str] = None
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    cc: Optional[List[str]] = None


@dataclass
class EmailResponse:
    code: int
    message: Optional[str] = None
