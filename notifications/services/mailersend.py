from typing import List, Dict, Any

from django.conf import settings
from mailersend import emails

from .base import EmailService
from ..exceptions import EmailServiceError
from ..types.email import EmailParams, EmailResponse


class MailerSendService(EmailService):
    def __init__(self):
        self.api_key = settings.MAILERSEND_API_KEY
        self.default_from_email = settings.DEFAULT_FROM_EMAIL
        self.default_from_name = settings.DEFAULT_FROM_NAME
        self._mailer = None

    @property
    def mailer(self):
        if self._mailer is None:
            self._mailer = emails.NewEmail(self.api_key)
        return self._mailer

    def _prepare_recipients(self, emails_list: List[str]) -> List[Dict[str, str]]:
        return [{"email": email} for email in emails_list]

    def _prepare_email(self, email_params: EmailParams) -> Dict[str, Any]:
        body = {}

        mail_from = {
            "email": self.default_from_email,
            "name": self.default_from_name,
        }

        reply_to = {
            "email": email_params.from_email or self.default_from_email,
            "name": email_params.from_name or self.default_from_name,
        }

        recipients = self._prepare_recipients(email_params.to_email)
        cc_list = self._prepare_recipients(email_params.cc) if email_params.cc else None

        self.mailer.set_mail_from(mail_from, body)
        self.mailer.set_mail_to(recipients, body)
        self.mailer.set_reply_to(reply_to, body)

        if cc_list:
            self.mailer.set_cc_recipients(cc_list, body)

        self.mailer.set_subject(email_params.subject, body)
        self.mailer.set_plaintext_content(email_params.content, body)

        if email_params.html_content:
            self.mailer.set_html_content(email_params.html_content, body)

        return body

    def send_email(self, email_params: EmailParams) -> EmailResponse:
        body = self._prepare_email(email_params)
        response = self.mailer.send(body)
        response_code = int(response[0:3])

        if response_code != 202:
            response_message = response[3:-1]
            raise EmailServiceError(
                f"code: {response_code}, detail: {response_message}"
            )

        return EmailResponse(code=response_code)
