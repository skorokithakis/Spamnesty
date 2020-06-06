import json
import os

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from ..models import Domain
from ..models import Message
from ..models import ReplyTemplate


class SmokeTests(TestCase):
    def test_urls(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)


class WebhookTests(TestCase):
    def setUp(self):
        Domain.objects.create(name="example.com", company_name="Company")
        ReplyTemplate.objects.create(body="Hello!")

    def test_invalid_forwarding(self):
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(
            reverse("main:email-webhook"),
            data={
                "addresses[from]": "hi@example.com",
                "addresses[to]": "sp@mnesty.com",
                "body[text]": "Hello",
                "id": "2",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("didn't work out", mail.outbox[0].subject)

    def test_forwarding_request(self):
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(
            reverse("main:email-webhook"),
            data=json.load(open("main/tests/forward_requests/1.json")),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("from\nhi@test.com.", mail.outbox[0].body)
        self.assertIn("CEO, Company", mail.outbox[1].body)

        mail.outbox = []

        response = self.client.post(
            reverse("main:email-webhook"),
            data=json.load(open("main/tests/forward_requests/1.json")),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 0)

        mail.outbox = []

        # A blacklisted email.
        response = self.client.post(
            reverse("main:email-webhook"),
            data=json.load(open("main/tests/forward_requests/2.json")),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 0)

    def test_forwarding_request_bulk(self):
        DIR = "main/tests/forward_requests/"
        for infile in os.listdir(DIR):
            if not infile.endswith(".json"):
                continue

            mail.outbox = []
            self.assertEqual(len(mail.outbox), 0)

            print(f"Processing {infile}...")

            response = self.client.post(
                reverse("main:email-webhook"), data=json.load(open(DIR + infile))
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"OK")
            self.assertEqual(len(mail.outbox), 2)

    def test_email_request(self):
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(
            reverse("main:email-webhook"),
            data=json.load(open("main/tests/email_requests/1.json")),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 0)

        self.assertEqual(Message.objects.exclude(send_on=None).count(), 1)

        # An email where the sender is us.
        response = self.client.post(
            reverse("main:email-webhook"),
            data=json.load(open("main/tests/email_requests/2.json")),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 0)

        self.assertEqual(Message.objects.exclude(send_on=None).count(), 1)
