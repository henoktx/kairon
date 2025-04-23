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

        self.assertTrue(result)

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
                to_email=self.test_email,
                subject=self.test_subject,
                content=self.test_content,
                from_email=custom_from_email,
                from_name=custom_from_name,
            )
        )

        self.assertTrue(result)

        mock_mailer.set_mail_from.assert_called_once_with(
            {"email": settings.DEFAULT_FROM_EMAIL, "name": settings.DEFAULT_FROM_NAME},
            {},
        )
        mock_mailer.set_reply_to.assert_called_once_with(
            {"email": custom_from_email, "name": custom_from_name}, {}
        )

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_with_cc_bcc(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "202"
        mock_new_email.return_value = mock_mailer

        cc = ["cc@test.com"]
        bcc = ["bcc@test.com"]

        result = self.service.send_email(
            EmailParams(
                to_email=self.test_email,
                subject=self.test_subject,
                content=self.test_content,
                cc=cc,
                bcc=bcc,
            )
        )

        self.assertTrue(result)

        mock_mailer.set_cc_recipients.assert_called_once_with(
            [{"email": "cc@test.com"}], {}
        )
        mock_mailer.set_bcc_recipients.assert_called_once_with(
            [{"email": "bcc@test.com"}], {}
        )

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_with_template(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "202"
        mock_new_email.return_value = mock_mailer

        template_id = "template123"

        result = self.service.send_email(
            EmailParams(
                to_email=self.test_email,
                subject=self.test_subject,
                content=self.test_content,
                template_id=template_id,
            )
        )

        self.assertTrue(result)

        mock_mailer.set_template.assert_called_once_with(template_id, {})

        mock_mailer.set_subject.assert_not_called()
        mock_mailer.set_plaintext_content.assert_not_called()

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_api_error(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.side_effect = RuntimeError("API Error")
        mock_new_email.return_value = mock_mailer

        with self.assertRaises(EmailServiceError) as context:
            self.service.send_email(
                EmailParams(
                    to_email=self.test_email,
                    subject=self.test_subject,
                    content=self.test_content,
                )
            )

        self.assertIn("Falha ao enviar email", str(context.exception))

    @patch("notifications.services.mailersend.emails.NewEmail")
    def test_send_email_non_202_response(self, mock_new_email):
        mock_mailer = MagicMock()
        mock_mailer.send.return_value = "400"
        mock_new_email.return_value = mock_mailer

        result = self.service.send_email(
            EmailParams(
                to_email=self.test_email,
                subject=self.test_subject,
                content=self.test_content,
            )
        )

        self.assertFalse(result)

    def test_service_initialization(self):
        self.assertEqual(self.service.api_key, settings.MAILERSEND_API_KEY)
        self.assertEqual(self.service.default_from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(self.service.default_from_name, settings.DEFAULT_FROM_NAME)
        self.assertIsNone(self.service._mailer)
