from typing import List, Optional, Dict
from django.conf import settings
from mailersend import emails
from .base import EmailService
from .exceptions import EmailServiceError


class MailerSendService(EmailService):
    def __init__(self):
        self.api_key = settings.MAILERSEND_API_KEY
        self.default_from_email = settings.DEFAULT_FROM_EMAIL
        self.default_from_name = settings.DEFAULT_FROM_NAME
        self.mailer = emails.NewEmail(self.api_key)

    def _prepare_recipients(self, emails_list: List[str]) -> List[Dict[str, str]]:
        return [{"email": email} for email in emails_list]

    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        from_name: str,
        from_email: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        template_id: Optional[str] = None,
    ) -> bool:
        try:
            body = {}

            mail_from = {
                "email": self.default_from_email,
                "name": self.default_from_name,
            }

            reply_to = {"email": from_email, "name": from_name}

            recipients = self._prepare_recipients([to_email])
            cc_list = self._prepare_recipients(cc) if cc else None
            bcc_list = self._prepare_recipients(bcc) if bcc else None

            self.mailer.set_mail_from(mail_from, body)
            self.mailer.set_mail_to(recipients, body)
            self.mailer.set_reply_to(reply_to, body)

            if cc_list:
                self.mailer.set_cc_recipients(cc_list, body)
            if bcc_list:
                self.mailer.set_bcc_recipients(bcc_list, body)

            if template_id:
                self.mailer.set_template(template_id, body)
            else:
                self.mailer.set_subject(subject, body)
                self.mailer.set_plaintext_content(content, body)

            response = self.mailer.send(body)
            return response.status_code == 202

        except Exception as e:
            raise EmailServiceError(f"Erro ao enviar email: {str(e)}")

    def send_bulk_email(
        self,
        to_emails: List[str],
        subject: str,
        content: str,
        from_email: str,
        template_id: Optional[str] = None,
    ) -> bool:
        try:
            body = {}

            mail_from = {
                "email": from_email or self.default_from_email,
                "name": self.default_from_name,
            }

            recipients = self._prepare_recipients(to_emails)

            self.mailer.set_mail_from(mail_from, body)
            self.mailer.set_recipients(recipients, body)

            if template_id:
                self.mailer.set_template(template_id, body)
            else:
                self.mailer.set_subject(subject, body)
                self.mailer.set_plaintext_content(content, body)

            response = self.mailer.send(body)
            return response.status_code == 202

        except Exception as e:
            raise EmailServiceError(f"Erro ao enviar emails em massa: {str(e)}")
