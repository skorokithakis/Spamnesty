from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class SmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'user',
            'user@user.com',
            'password'
        )
        self.user.is_staff = True
        self.user.save()

    def test_urls(self):
        response = self.client.get(reverse("classification:classify"))
        self.assertEqual(response.status_code, 404)

        self.client.login(username="user", password="password")

        response = self.client.get(reverse("classification:classify"))
        self.assertEqual(response.status_code, 200)
