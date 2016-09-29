from __future__ import unicode_literals

import shortuuid
from django.db import models
from django.db.utils import IntegrityError
from email.utils import parseaddr
from faker import Faker

from email.utils import make_msgid
from django.core.mail import EmailMessage


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
            conversation = super().create()
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


class Domain(CharIDModel):
    "A domain to use for sending and receiving email."
    # The domain name (e.g. example.com).
    name = models.CharField(max_length=1000)
    # The company name (e.g. Example, LLC).
    company_name = models.CharField(max_length=1000)

    def __str__(self):
        return "{0.company_name} ({0.name})".format(self)


class Conversation(CharIDModel):
    """The main conversation object."""
    # The name of our sender (the bot).
    sender_name = models.CharField(max_length=1000, default=generate_fake_name)

    # The fake domain to use to send mail from.
    domain = models.ForeignKey(Domain, default=get_random_domain)

    objects = ConversationManager()

    def __str__(self):
        return "%s <%s>" % (self.sender_name, self.sender_email)

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

    # The plaintext body of the email.
    body = models.TextField()

    # The body of the email, stripped of any replies or signatures.
    stripped_body = models.TextField(blank=True)

    # The signature of the email, if available.
    stripped_signature = models.TextField(blank=True)

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
        return parseaddr(self.sender)[0]

    @property
    def sender_email(self):
        "Parse and return the sender's email address."
        if not self.sender:
            return ""
        return parseaddr(self.sender)[1]

    @property
    def recipient_name(self):
        "Parse and return the recipient's name."
        if not self.recipient:
            return ""
        return parseaddr(self.recipient)[0]

    @property
    def recipient_email(self):
        "Parse and return the recipient's email address."
        if not self.recipient:
            return ""
        return parseaddr(self.recipient)[1]

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
        message.stripped_body = posted["stripped-text"]
        message.stripped_signature = posted.get("stripped-signature", "")
        message.message_id = posted["Message-Id"]
        message.in_reply_to = posted.get("In-Reply-To", "")
        message.save()

        return message

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

    def save(self, *args, **kwargs):
        "Generate a message ID on saving."
        if not self.conversation_id:
            # In order to get_by_message, we need to already have set in_reply_to.
            self.conversation = Conversation.objects.get_by_message(self)

        if not self.message_id:
            self.message_id = generate_message_id(self.conversation.domain.name)

        super().save(*args, **kwargs)
