from abc import ABC, abstractmethod

from ..types.email import EmailParams, EmailResponse


class EmailService(ABC):
    @abstractmethod
    def send_email(self, email_params: EmailParams) -> EmailResponse:
        pass
