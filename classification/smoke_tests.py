from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from main.models import Conversation
from main.models import Domain


class SmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "user@user.com", "password")
        self.user.is_staff = True
        self.user.save()

    def test_urls(self):
        response = self.client.get(reverse("classification:classify"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue("login" in response.url)

        self.client.login(username="user", password="password")

        response = self.client.get(reverse("classification:classify"))
        self.assertEqual(response.status_code, 200)

        self.client.logout()

        response = self.client.post(reverse("classification:delete"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue("login" in response.url)


class DeleteTests(TestCase):
    def setUp(self):
        Domain.objects.create(name="example.com", company_name="Company")
        self.user = User.objects.create_user("user", "user@user.com", "password")
        self.user.is_staff = True
        self.user.save()

    def test_delete(self):

        conversation = Conversation.objects.create()
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("classification:delete"), data={"conversation_id": conversation.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertRaises(
            Conversation.DoesNotExist, Conversation.objects.get, id=conversation.id
        )

        response = self.client.post(
            reverse("classification:delete"), data={"conversation_id": conversation.id}
        )
        self.assertEqual(response.status_code, 404)
