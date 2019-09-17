from django.test import TestCase
from main.models import Domain, Message
from main.utils import check_last_messages_similarity, get_similarity


class SimilarityTextTests(TestCase):
    def test_simple_different(self):
        doc1 = "abc def ghi1"
        doc2 = "abc def xxx"
        similarity = get_similarity(doc1, doc2)
        self.assertLess(similarity, 1.0)

    def test_simple_name(self):
        doc1 = "abc def ghi1"
        similarity = get_similarity(doc1, doc1)
        self.assertGreaterEqual(similarity, 1.0)

    def test_bounce(self):
        doc1 = open("main/tests/blacklist_emails/spam_1a.txt").read()
        doc2 = open("main/tests/blacklist_emails/spam_1b.txt").read()
        similarity = get_similarity(doc1, doc2)
        self.assertGreaterEqual(similarity, 0.9)

    def test_repeat_text(self):
        # Test that repeated words do not affect the (cosine) similarity
        doc1 = "abc def ghi1"
        doc2 = doc1 + " " + doc1 + " " + doc1
        similarity = get_similarity(doc1, doc2)
        self.assertGreaterEqual(similarity, 1.0)

    def test_spam_bounce(self):
        # Test a "normal" spam body against a bounce
        doc1 = open("main/tests/blacklist_emails/spam_2.txt").read()
        doc2 = open("main/tests/blacklist_emails/spam_1b.txt").read()
        similarity = get_similarity(doc1, doc2)
        self.assertLess(similarity, 0.8)


class MessageTests(TestCase):
    def setUp(self):
        self.domain = Domain.objects.create()
        self.domain.save()

    def test_single_message(self):
        """Test that a single message is not similar to anything."""
        message1 = Message.objects.create(subject="subject", body="body", direction="F")
        conversation = message1.conversation
        self.assertFalse(check_last_messages_similarity(conversation))

    def test_single_message_with_reply(self):
        """A single spammer message with our reply is not similar to anything."""
        subject = "subject"
        body = "body1"
        message1 = Message.objects.create(subject=subject, body=body, direction="F")
        conversation = message1.conversation
        self.assertFalse(check_last_messages_similarity(conversation))
        body = "body2"
        Message.objects.create(
            subject=subject,
            body=body,
            direction="S",
            conversation_id=message1.conversation_id,
        )
        self.assertFalse(check_last_messages_similarity(conversation))

    def test_two_messages_with_reply(self):
        """Two dissimilar spammer messages."""
        subject = "subject"
        body = "body1"
        message1 = Message.objects.create(subject=subject, body=body, direction="F")
        conversation = message1.conversation
        self.assertFalse(check_last_messages_similarity(conversation))
        body = "body2"
        message2 = Message.objects.create(
            subject=subject,
            body=body,
            direction="S",
            conversation_id=message1.conversation_id,
        )
        message2.save()
        self.assertFalse(check_last_messages_similarity(conversation))
        body = "body3"
        message3 = Message.objects.create(
            subject=subject,
            body=body,
            direction="R",
            conversation_id=message1.conversation_id,
        )
        message3.save()
        self.assertFalse(check_last_messages_similarity(conversation))

    def test_two_similar_messages_with_reply(self):
        """Two dissimilar spammer messages."""
        subject = "subject"
        body = "body1"
        message1 = Message.objects.create(subject=subject, body=body, direction="F")
        conversation = message1.conversation
        self.assertFalse(check_last_messages_similarity(conversation))
        body = "body2"
        message2 = Message.objects.create(
            subject=subject,
            body=body,
            direction="S",
            conversation_id=message1.conversation_id,
        )
        message2.save()
        self.assertFalse(check_last_messages_similarity(conversation))
        body = "body1"
        message3 = Message.objects.create(
            subject=subject,
            body=body,
            direction="R",
            conversation_id=message1.conversation_id,
        )
        message3.save()
        self.assertTrue(check_last_messages_similarity(conversation))
