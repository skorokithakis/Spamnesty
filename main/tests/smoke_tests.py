from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse


class SmokeTests(TestCase):
    def test_urls(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)


class WebhookTests(TestCase):
    def test_forwarding(self):
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(reverse("main:forwarded-webhook"), data={"From": "hi@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("didn't work out", mail.outbox[0].subject)
