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
            {
                "body": open("main/tests/forwarded_emails/6.txt").read(),
                "sender": "Spam Spammer <spam@example.com>",
                "check": "Hi, this is spam.",
            },
            {
                "body": open("main/tests/forwarded_emails/7.txt").read(),
                "sender": "stuff/things <reply+00005c60909823812093819034c0f36b6e0bb2b65fda05b292cf000000011406c76b92a169ce020bbb75@reply.example.com>",
                "check": "You could try to create",
            },
            {
                "body": open("main/tests/forwarded_emails/8.txt").read(),
                "sender": "stuff/things <reply+00005c60909823812093819034c0f36b6e0bb2b65fda05b292cf000000011406c76b92a169ce020bbb75@reply.example.com>",
                "check": "You could try to create",
            },
        ]

        for message in messages:
            sender, body = parse_forwarded_message(message["body"])
            self.assertEqual(sender, message["sender"])
            self.assertIn(message["check"], body)

    def test_address_parsing(self):
        addresses = [
            ('"Test Tester" <test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester <test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester<test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester <test@example.com<mailto:test@example.com>>', "Test Tester", "test@example.com"),
            ('test@example.com', "", "test@example.com"),
            ('<test@example.com>', "", "test@example.com"),
        ]
        for address, name, email in addresses:
            n, e = parse_email_address(address)
            self.assertEqual(n, name)
            self.assertEqual(e, email)
