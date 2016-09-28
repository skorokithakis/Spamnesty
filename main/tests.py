from django.test import TestCase
from django.core.urlresolvers import reverse
from hypothesis.extra.django.models import models, default_value
import hypothesis.strategies as st

from .models import Conversation


ConversationFactory = models(
        Conversation,
        id=default_value,
        sender_name=st.text(max_size=100),
    )


class SmokeTests(TestCase):
    def setUp(self):
        self.conversation1 = ConversationFactory.example()
        self.conversation2 = ConversationFactory.example()

    def test_urls(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
