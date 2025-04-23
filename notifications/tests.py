from unittest.mock import patch, MagicMock

from django.conf import settings
from django.test import TestCase

from .exceptions import EmailServiceError
from .services.mailersend import MailerSendService
from .types.email import EmailParams


class TestMailerSendService(TestCase):
    def setUp(self):
        settings.MAILERSEND_API_KEY = "test_api_key"
        settings.DEFAULT_FROM_EMAIL = "default@test.com"
        settings.DEFAULT_FROM_NAME = "Test Sender"

        self.service = MailerSendService()

        self.test_email = "recipient@test.com"
        self.test_subject = "Test Subject"
        self.test_content = "Test Content"

    def test_prepare_recipients_single_email(self):
        emails = ["test@example.com"]
        expected = [{"email": "test@example.com"}]
        result = self.service._prepare_recipients(emails)
        self.assertEqual(result, expected)

    def test_prepare_recipients_multiple_emails(self):
        emails = ["test1@example.com", "test2@example.com"]
        expected = [{"email": "test1@example.com"}, {"email": "test2@example.com"}]
        result = self.service._prepare_recipients(emails)
        self.assertEqual(result, expected)

    def test_prepare_recipients_empty_list(self):
        emails = []
        expected = []
        result = self.service._prepare_recipients(emails)
        self.assertEqual(result, expected)

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_basic_success(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "202"
        mock_new_email.return_value = mock_mailer

        result = self.service.send_email(
            EmailParams(
                to_email=[self.test_email],
                subject=self.test_subject,
                content=self.test_content,
            )
        )

        self.assertEqual(result.code, 202)

        mock_mailer.set_mail_from.assert_called_once_with(
            {"email": settings.DEFAULT_FROM_EMAIL, "name": settings.DEFAULT_FROM_NAME},
            {},
        )
        mock_mailer.set_mail_to.assert_called_once_with(
            [{"email": self.test_email}], {}
        )
        mock_mailer.set_reply_to.assert_called_once_with(
            {"email": settings.DEFAULT_FROM_EMAIL, "name": settings.DEFAULT_FROM_NAME},
            {},
        )
        mock_mailer.set_subject.assert_called_once_with(self.test_subject, {})
        mock_mailer.set_plaintext_content.assert_called_once_with(self.test_content, {})
        mock_mailer.send.assert_called_once_with({})

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_with_custom_from(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "202"
        mock_new_email.return_value = mock_mailer

        custom_from_email = "custom@test.com"
        custom_from_name = "Custom Sender"

        result = self.service.send_email(
            EmailParams(
                to_email=[self.test_email],  # Corrigido: deve ser uma lista
                subject=self.test_subject,
                content=self.test_content,
                from_email=custom_from_email,
                from_name=custom_from_name,
            )
        )

        self.assertEqual(result.code, 202)

        mock_mailer.set_mail_from.assert_called_once_with(
            {"email": settings.DEFAULT_FROM_EMAIL, "name": settings.DEFAULT_FROM_NAME},
            {},
        )
        mock_mailer.set_reply_to.assert_called_once_with(
            {"email": custom_from_email, "name": custom_from_name}, {}
        )

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_with_cc(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "202"
        mock_new_email.return_value = mock_mailer

        cc = ["cc@test.com"]

        result = self.service.send_email(
            EmailParams(
                to_email=[self.test_email],  # Corrigido: deve ser uma lista
                subject=self.test_subject,
                content=self.test_content,
                cc=cc,
            )
        )

        self.assertEqual(result.code, 202)

        mock_mailer.set_cc_recipients.assert_called_once_with(
            [{"email": "cc@test.com"}], {}
        )

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_with_html_content(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "202"
        mock_new_email.return_value = mock_mailer

        html_content = "<p>Test HTML Content</p>"

        result = self.service.send_email(
            EmailParams(
                to_email=[self.test_email],
                subject=self.test_subject,
                content=self.test_content,
                html_content=html_content,
            )
        )

        self.assertEqual(result.code, 202)
        mock_mailer.set_html_content.assert_called_once_with(html_content, {})

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_api_error(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "500 Internal Server Error"
        mock_new_email.return_value = mock_mailer

        with self.assertRaises(EmailServiceError) as context:
            self.service.send_email(
                EmailParams(
                    to_email=[self.test_email],
                    subject=self.test_subject,
                    content=self.test_content,
                )
            )

        self.assertIn("code: 500", str(context.exception))

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_non_202_response(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "400 Bad Request"  # Simulando resposta de erro
        mock_new_email.return_value = mock_mailer

        with self.assertRaises(EmailServiceError) as context:
            self.service.send_email(
                EmailParams(
                    to_email=[self.test_email],
                    subject=self.test_subject,
                    content=self.test_content,
                )
            )

        self.assertIn("code: 400", str(context.exception))

    def test_service_initialization(self):
        self.assertEqual(self.service.api_key, settings.MAILERSEND_API_KEY)
        self.assertEqual(self.service.default_from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(self.service.default_from_name, settings.DEFAULT_FROM_NAME)
        self.assertIsNone(self.service._mailer)
