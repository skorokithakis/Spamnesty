import json

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse

from ..models import Domain, ReplyTemplate, Message


class SmokeTests(TestCase):
    def test_urls(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)


class WebhookTests(TestCase):
    def setUp(self):
        Domain.objects.create(name="Example", company_name="Company")
        ReplyTemplate.objects.create(body="Hello!")

    def test_invalid_forwarding(self):
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(reverse("main:forwarded-webhook"), data={"From": "hi@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("didn't work out", mail.outbox[0].subject)

    def test_forwarding_request(self):
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(reverse("main:forwarded-webhook"), data=json.load(open("main/tests/forward_requests/1.json")))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("from\nhi@example.com.", mail.outbox[0].body)
        self.assertIn("CEO, Company", mail.outbox[1].body)

    def test_email_request(self):
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(reverse("main:email-webhook"), data=json.load(open("main/tests/email_requests/1.json")))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 0)

        self.assertEqual(Message.objects.exclude(send_on=None).count(), 1)
