from __future__ import unicode_literals

import datetime
import re
import random

import shortuuid
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.db.utils import IntegrityError
from django.urls import reverse
from email.utils import make_msgid
from faker import Faker

from .utils import parse_forwarded_message, parse_email_address


def generate_message_id(domain_name) -> str:
    "Generate an email message ID."
    return make_msgid(domain=domain_name)


def generate_fake_name():
    "Generate a fake name."
    return Faker().name()


def generate_uuid() -> str:
    "Generate a UUID for an object."
    return shortuuid.ShortUUID("abdcefghjkmnpqrstuvwxyz").random()[:8]


def get_random_domain():
    "Choose a random domain from the database."
    return Domain.objects.order_by("?").first()


class CharIDModel(models.Model):
    """Base model that gives children string IDs."""
    id = models.CharField(max_length=30, primary_key=True,
            default=generate_uuid, editable=False)

    class Meta:
        abstract = True


class Domain(CharIDModel):
    "A domain to use for sending and receiving email."
    # The domain name (e.g. example.com).
    name = models.CharField(max_length=1000)
    # The company name (e.g. Example, LLC).
    company_name = models.CharField(max_length=1000)

    def __str__(self):
        return "{0.company_name} ({0.name})".format(self)


class ConversationManager(models.Manager):
    def create(self, *args, **kwargs):
        """Generate an object, retrying if there's an ID collision."""

        # Try to generate new IDs for the object if one collides.
        tries = 10
        for x in range(tries):
            try:
                obj = super().create(*args, **kwargs)
            except IntegrityError:
                continue
            else:
                break
        else:
            raise IntegrityError("Could not find an ID after %s tries." % tries)

        return obj

    def get_by_message(self, message):
        """
        Accept a message and try to discover the conversation it belongs to.

        Return an existing Conversation instance, if the message is a reply to
        one of the messages we've already seen, or a new Conversation instance
        if the message is new or has just been forwarded.

        The message instance that is passed in need not be saved or have a
        conversation property set, although it should have the in_reply_to
        property set, if possible.
        """
        if message.direction == "F":
            # A forwarded email gets a new conversation.
            conversation = self.create()
        else:
            replied_to = Message.objects.filter(message_id=message.in_reply_to).first()
            if not replied_to:
                # We've never seen this ID before, so return a new conversation.
                conversation = super().create()
            else:
                # If we've seen a message with that ID before, return its
                # conversation.
                conversation = replied_to.conversation
        return conversation


class Conversation(CharIDModel):
    """The main conversation object."""
    # The email address of the person who reported this message.
    reporter_email = models.CharField(max_length=1000, blank=True)

    # The name of our sender (the bot).
    sender_name = models.CharField(max_length=1000, default=generate_fake_name)

    # The fake domain to use to send mail from.
    domain = models.ForeignKey(Domain, default=get_random_domain)

    objects = ConversationManager()

    def __str__(self):
        return "%s <%s>" % (self.sender_name, self.sender_email)

    def get_absolute_url(self):
        return reverse("main:conversation-view", args=[self.id])

    @property
    def sender_username(self):
        "Derive a username from the sender's name."
        split_name = self.sender_name.split()
        return (split_name[0][0] + split_name[1]).lower()

    @property
    def sender_email(self):
        "Derive a username from the sender's username."
        return "%s@%s" % (self.sender_username, self.domain.name)


class Message(CharIDModel):
    """A single email message."""
    DIRECTIONS = [("F", "Forwarded"), ("S", "Sent"), ("R", "Received")]

    timestamp = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(Conversation)

    # Whether this email was forwarded to us, sent by us, or received by us from
    # the spammer.
    direction = models.CharField(choices=DIRECTIONS, max_length=10)

    sender = models.CharField(max_length=1000, blank=True)
    recipient = models.CharField(max_length=1000, blank=True)
    subject = models.CharField(max_length=1000)

    # The time to send the email on.
    send_on = models.DateTimeField(blank=True, null=True)

    # The plaintext body of the email.
    body = models.TextField()

    # The body of the email, with signature.
    stripped_body = models.TextField(blank=True)

    # The message ID, so we can keep track of the conversation.
    message_id = models.CharField(max_length=1000, unique=True)

    # The in-reply-to header, which complements the ID.
    in_reply_to = models.CharField(max_length=1000, blank=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return self.subject

    @property
    def sender_name(self):
        "Parse and return the sender's name."
        if not self.sender:
            return ""
        return parse_email_address(self.sender)[0]

    @property
    def sender_email(self):
        "Parse and return the sender's email address."
        if not self.sender:
            return ""
        return parse_email_address(self.sender)[1]

    @property
    def recipient_name(self):
        "Parse and return the recipient's name."
        if not self.recipient:
            return ""
        return parse_email_address(self.recipient)[0]

    @property
    def recipient_email(self):
        "Parse and return the recipient's email address."
        if not self.recipient:
            return ""
        return parse_email_address(self.recipient)[1]

    @classmethod
    def parse_from_mailgun(cls, posted, forwarded=False):
        """
        Parse a message from Mailgun and return a Message instance.
        """
        message = cls()
        message.direction = "F" if forwarded else "R"
        message.sender = posted["From"]
        message.recipient = posted["To"]
        message.subject = posted["Subject"]
        message.body = posted["body-plain"]
        message.stripped_body = posted.get("stripped-text", "")
        message.message_id = posted["Message-Id"]
        message.in_reply_to = posted.get("In-Reply-To", "")

        if forwarded:
            # If a message has been forwarded to us, we need to:
            #
            # 1. Store the original reporter's email in the conversation, so we
            #    can email them.
            # 2. Parse the forwarded message from the email and replace the body
            #    of the email with it.
            # 3. Parse the spammer's email from it and replace the sender with
            #    that.
            # 4. Remove the "Fwd:" from the subject.
            #
            # We will consider the forwarded message to be what starts the email
            # chain.

            # Parse the forwarded message and replace the sender and body.
            body = message.stripped_body if message.stripped_body else message.body
            sender, body = parse_forwarded_message(body)
            if not sender:
                # We couldn't locate a sender, so abort.
                return None
            message.sender = sender
            message.body = message.stripped_body = body

            # Strip Fw/Fwd from the subject.
            match = re.match("\W*Fwd?: (.*)$", message.subject, re.I)
            if match:
                message.subject = match.group(1)

            message.conversation = Conversation.objects.create(
                reporter_email=posted["From"]
            )

        message.save()

        return message

    def queue(self):
        """
        Queue the message for sending with a random delay (to appear more
        realistic).
        """
        if settings.DEBUG:
            send_on = datetime.datetime.now()
        else:
            send_on = datetime.datetime.now() + \
                datetime.timedelta(seconds=random.randrange(60, 12 * 60 * 60))
        self.send_on = send_on
        self.save()

    def send(self):
        "Send the message through email."
        conversation = self.conversation

        email = EmailMessage(
            self.subject,
            self.body,
            "%s <%s>" % (conversation.sender_name, self.conversation.sender_email),
            [self.recipient],
            headers={'Message-ID': self.message_id},
        )

        email.send()

        self.send_on = None
        self.save()

    def save(self, *args, **kwargs):
        "Generate a message ID on saving."
        if not self.conversation_id:
            # In order to get_by_message, we need to already have set in_reply_to.
            self.conversation = Conversation.objects.get_by_message(self)

        if not self.message_id:
            self.message_id = generate_message_id(self.conversation.domain.name)

        super().save(*args, **kwargs)
