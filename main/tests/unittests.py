from django.test import TestCase
from django.core.urlresolvers import reverse

from ..utils import parse_forwarded_message


class UnitTests(TestCase):
    def test_parsing(self):
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
        ]

        for message in messages:
            sender, body = parse_forwarded_message(message["body"])
            self.assertEqual(sender, message["sender"])
            self.assertIn(message["check"], body)
