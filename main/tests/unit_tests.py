from django.test import TestCase

from ..utils import parse_email_address, parse_forwarded_message


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
            {
                "body": open("main/tests/forwarded_emails/9.txt").read(),
                "sender": "International Thing of Thing Stuff <j.thing@example.com>",
                "check": "You could try to create",
            },
            {
                "body": open("main/tests/forwarded_emails/10.txt").read(),
                "sender": "Example <ex@example.com>",
                "check": "There was stuff",
            },
            {
                "body": open("main/tests/forwarded_emails/11.txt").read(),
                "sender": "reply.912.45705@example.com",
                "check": "Do your password reset requests",
            },
            {
                "body": open("main/tests/forwarded_emails/12.txt").read(),
                "sender": "adminuyuog836 <peyveoext160314@mail.com>",
                "check": "Message",
            },
            {
                "body": open("main/tests/forwarded_emails/13.txt").read(),
                "sender": "Bamba Mariam <bamba@gmail.com>",
                "check": "Things",
            },
            {
                "body": open("main/tests/forwarded_emails/14.txt").read(),
                "sender": "Rev Fr Andrew Bob <revfatherbob@hotmale.com>",
                "check": "spam content",
            },
            {
                "body": open("main/tests/forwarded_emails/15.txt").read(),
                "sender": "John Doe <Ofux@44.34.65.218.broad.nc.jx.dynamic.163data.com.cn>",
                "check": "More stuff",
            },
            {
                "body": open("main/tests/forwarded_emails/16.txt").read(),
                "sender": "E. Xample <ex@example.com>",
                "check": "Hello",
            },
            {
                "body": open("main/tests/forwarded_emails/17.txt").read(),
                "sender": "E. Xample <ex@example.com>",
                "check": "Mail here",
            },
        ]

        for message in messages:
            sender, body = parse_forwarded_message(message["body"])
            self.assertEqual(sender, message["sender"])
            self.assertIn(message["check"], body)

    def test_address_parsing(self):
        addresses = [
            ('"Test Tester" <test@example.com>', "Test Tester", "test@example.com"),
            ('"Test Tester" <test@example.com>stuff.com', None, None),
            ('Test Tester <test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester <test@example.com>other.stuff.com', None, None),
            ('Test Tester [test@example.com]', "Test Tester", "test@example.com"),
            ('Test Tester test@example.com', "Test Tester", "test@example.com"),
            ('Test Tester (test@example.com)', "Test Tester", "test@example.com"),
            ('Test Tester (mailto:test@example.com)', "Test Tester", "test@example.com"),
            ('Test Tester <mailto:test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester [mailto:test@example.com]', "Test Tester", "test@example.com"),
            ('Test Tester <<test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester <<<<<test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester <test@example.com>>>>>', "Test Tester", "test@example.com"),
            ('FBI OFFICE <"WWW."@ex.amp.le.com>', "FBI OFFICE", '"WWW."@ex.amp.le.com'),
            ('Test Tester <<<<test@example.com>>>>>', "Test Tester", "test@example.com"),
            ('Test Tester<test@example.com>', "Test Tester", "test@example.com"),
            ('Test Tester <test@example.com<mailto:test@example.com>>', "Test Tester", "test@example.com"),
            ('test@example.com', "", "test@example.com"),
            ('<test@example.com>', "", "test@example.com"),
            ('<mailto:test@example.com>', "", "test@example.com"),
            ('Example Example [mailto:exa.mple@example.com]', "Example Example", "exa.mple@example.com"),
        ]
        for address, name, email in addresses:
            if name is None:
                with self.assertRaises(ValueError):
                    parse_email_address(address)
            else:
                n, e = parse_email_address(address)
                self.assertEqual(n, name)
                self.assertEqual(e, email)
