from django.test import TestCase
from django.core.urlresolvers import reverse


class SmokeTests(TestCase):
    def test_urls(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
