from django.test import TestCase

from ..utils import parse_email_address
from ..utils import parse_forwarded_message


class UnitTests(TestCase):
    def test_message_parsing(self):
        messages = [
            {"sender": "ex@example.com <ex@example.com>", "check": "Mail body"},
            {"sender": "as@example.com <as@example.com>", "check": "looking for stuff"},
            {"sender": "SomePerson <sperson@example.com>", "check": "Stuff."},
            {
                "sender": "MRS ELIZABETH JOHNSON <elizjohnson@example.com>",
                "check": "PLEASE YOUR URGENT RESPONSE",
            },
            {"sender": "SomePerson <sperson@example.com>", "check": "Stuff."},
            {"sender": "SomePerson <sperson@example.com>", "check": "Stuff."},
            {"sender": "Spam Spammer <spam@example.com>", "check": "Hi, this is spam."},
            {
                "sender": "stuff/things <reply+00005c60909823812093819034c0f36b6e0bb2b65fda05b292cf000000011406c76b92a169ce020bbb75@reply.example.com>",
                "check": "You could try to create",
            },
            {
                "sender": "stuff/things <reply+00005c60909823812093819034c0f36b6e0bb2b65fda05b292cf000000011406c76b92a169ce020bbb75@reply.example.com>",
                "check": "You could try to create",
            },
            {
                "sender": "International Thing of Thing Stuff <j.thing@example.com>",
                "check": "You could try to create",
            },
            {"sender": "Example <ex@example.com>", "check": "There was stuff"},
            {
                "sender": "reply.912.45705@example.com",
                "check": "Do your password reset requests",
            },
            {"sender": "adminuyuog836 <peyveoext160314@mail.com>", "check": "Message"},
            {"sender": "Bamba Mariam <bamba@gmail.com>", "check": "Things"},
            {
                "sender": "Rev Fr Andrew Bob <revfatherbob@hotmale.com>",
                "check": "spam content",
            },
            {
                "sender": "John Doe <Ofux@44.34.65.218.broad.nc.jx.dynamic.163data.com.cn>",
                "check": "More stuff",
            },
            {"sender": "E. Xample <ex@example.com>", "check": "Hello"},
            {"sender": "E. Xample <ex@example.com>", "check": "Mail here"},
            {
                "sender": "cj002@tradexunpan.com <cj002@tradexunpan.com>",
                "check": "Mail body",
            },
            {"sender": "Ex Ample <ex@example.com>", "check": "Mail body"},
            {
                "sender": "Yoon Patty (US Partners) <patty.yoon@partners.mcd.com>",
                "check": "Mail body",
            },
            {
                "sender": "Adam Collins Service <aaliah37@example.com>",
                "check": "Don't want to receive",
            },
        ]

        for counter, message in enumerate(messages):
            print("Testing %s..." % counter)
            sender, body = parse_forwarded_message(
                open("main/tests/forwarded_emails/%s.txt" % counter).read()
            )
            self.assertEqual(sender, message["sender"])
            self.assertIn(message["check"], body)

    def test_address_parsing(self):
        addresses = [
            ('"Test Tester" <test@example.com>', "Test Tester", "test@example.com"),
            ('"Test Tester" <test@>stuff.com', None, None),
            ("Test Tester <test@example.com>", "Test Tester", "test@example.com"),
            (
                "test@example.com [mailto:test@example.com] On Behalf Of Whoever",
                "test@example.com",
                "test@example.com",
            ),
            (
                "Test Tester <test@example.com> On behalf of whoever",
                "Test Tester",
                "test@example.com",
            ),
            ("Test Tester [test@example.com]", "Test Tester", "test@example.com"),
            ("Test Tester test@example.com", "Test Tester", "test@example.com"),
            ("Test Tester (test@example.com)", "Test Tester", "test@example.com"),
            (
                "Test Tester (mailto:test@example.com)",
                "Test Tester",
                "test@example.com",
            ),
            (
                "Test Tester <mailto:test@example.com>",
                "Test Tester",
                "test@example.com",
            ),
            (
                "Test Tester [mailto:test@example.com]",
                "Test Tester",
                "test@example.com",
            ),
            ("Test Tester <<test@example.com>", "Test Tester", "test@example.com"),
            ("Test Tester <<<<<test@example.com>", "Test Tester", "test@example.com"),
            ("Test Tester <test@example.com>>>>>", "Test Tester", "test@example.com"),
            ('FBI OFFICE <"WWW."@ex.amp.le.com>', "FBI OFFICE", '"WWW."@ex.amp.le.com'),
            (
                "Test Tester <<<<test@example.com>>>>>",
                "Test Tester",
                "test@example.com",
            ),
            ("Test Tester<test@example.com>", "Test Tester", "test@example.com"),
            (
                '"Adam ... the last of the Clan Mantobeus" <test@example.com>',
                "Adam ... the last of the Clan Mantobeus",
                "test@example.com",
            ),
            ("test@example.com", "", "test@example.com"),
            ("<test@example.com>", "", "test@example.com"),
            ("<mailto:test@example.com>", "", "test@example.com"),
            (
                "Example Example [mailto:exa.mple@example.com]",
                "Example Example",
                "exa.mple@example.com",
            ),
        ]
        for address, name, email in addresses:
            if name is None:
                with self.assertRaises(ValueError):
                    n, e = parse_email_address(address)
            else:
                n, e = parse_email_address(address)
                self.assertEqual(n, name)
                self.assertEqual(e, email)
