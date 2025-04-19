from abc import ABC, abstractmethod
from typing import List, Optional


class EmailService(ABC):
    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        from_name: Optional[str] = None,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        template_id: Optional[str] = None,
    ) -> bool:
        pass

    @abstractmethod
    def send_bulk_email(
        self,
        to_emails: List[str],
        subject: str,
        content: str,
        from_name: Optional[str] = None,
        from_email: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> bool:
        pass
