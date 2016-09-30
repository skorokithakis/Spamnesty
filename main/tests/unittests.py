from django.test import TestCase

from ..utils import parse_forwarded_message, parse_email_address


class UnitTests(TestCase):
    def test_message_parsing(self):
        messages = [
            {
                "body": open("main/tests/forwarded_emails/1.txt").read(),
                "sender": "as@example.com <as@example.com>",
                "check": "looking for stuff",
            },
            {
                "body": open("main/tests/forwarded_emails/2.txt").read(),
                "sender": "SomePerson <sperson@example.com>",
                "check": "Stuff.",
            },
            {
                "body": open("main/tests/forwarded_emails/3.txt").read(),
                "sender": "MRS ELIZABETH JOHNSON <elizjohnson@example.com>",
                "check": "PLEASE YOUR URGENT RESPONSE",
            },
            {
                "body": open("main/tests/forwarded_emails/4.txt").read(),
                "sender": "SomePerson <sperson@example.com>",
                "check": "Stuff.",
            },
            {
                "body": open("main/tests/forwarded_emails/5.txt").read(),
                "sender": "SomePerson <sperson@example.com>",
                "check": "Stuff.",
            },
        ]

        for message in messages:
            sender, body = parse_forwarded_message(message["body"])
            self.assertEqual(sender, message["sender"])
            self.assertIn(message["check"], body)

    def test_address_parsing(self):
        addresses = [
            '"Test Tester" <test@example.com>',
            'Test Tester <test@example.com>',
        ]
        for address in addresses:
            name, email = parse_email_address(address)
            self.assertEqual(name, "Test Tester")
            self.assertEqual(email, "test@example.com")
