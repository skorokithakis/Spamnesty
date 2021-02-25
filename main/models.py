import base64
import datetime
import random
import re
import time
from email.utils import make_msgid

import shortuuid
import spintax
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.db.utils import IntegrityError
from django.urls import reverse
from faker import Faker

from .utils import is_blacklisted
from .utils import parse_email_address
from .utils import parse_forwarded_message


def is_base64(text: str) -> bool:
    """Guess whether text is base64-encoded."""
    return bool(
        re.match(
            r"^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$",
            text.replace("\n", ""),
        )
    )


def try_decoding_base64(text: str) -> str:
    """Try to decode some potentially base64 text, returning the original if decoding fails."""
    if not is_base64(text):
        return text
    return base64.b64decode(text.replace("\n", " ")).decode(errors="ignore")


def get_relevant_recipient(recipients: str) -> str:
    """
    Clean the recipients list and return the one we care about.

    Sometimes we'll get a comma-separated list of multiple recipients,
    and we want to ignore (and not display) everyone who's not on our
    domain. This function picks the relevant recipient and returns it.

    Returns jdoe@ourdomain if no relevant recipient was found.
    """
    domains = [d.name for d in Domain.objects.all()]
    for recipient in recipients.split(","):
        if any(True for domain in domains if f"@{domain}" in recipient):
            return recipient.strip()
    return f"jdoe@{domains[0]}"


def strip_html(html):
    """Strip all tags from an HTML string."""
    soup = BeautifulSoup(html, features="html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n" + br.text)
    return soup.text


def generate_message_id(domain_name) -> str:
    """Generate an email message ID."""
    return make_msgid(domain=domain_name)


def generate_fake_name():
    """Generate a fake name."""
    Faker.seed(time.time())
    fake = Faker()
    return fake.name()


def generate_key() -> str:
    """Generate a secret key for an object."""
    return shortuuid.ShortUUID().random()


def generate_uuid() -> str:
    """Generate a UUID for an object."""
    return shortuuid.ShortUUID("abdcefghjkmnpqrstuvwxyz").random()[:8]


def get_default_category() -> int:
    """Retrieve the default SpamCategory."""
    return SpamCategory.objects.get(default=True).id


def get_random_domain():
    """Choose a random domain from the database."""
    return Domain.objects.order_by("?").first()


class CharIDModel(models.Model):
    """Base model that gives children string IDs."""

    id = models.CharField(
        max_length=30, primary_key=True, default=generate_uuid, editable=False
    )

    class Meta:
        abstract = True


class Domain(CharIDModel):
    """A domain to use for sending and receiving email."""

    # The domain name (e.g. example.com).
    name = models.CharField(max_length=1000)
    # The company name (e.g. Example, LLC).
    company_name = models.CharField(max_length=1000)

    def __str__(self):
        return "{0.company_name} ({0.name})".format(self)


class SpamCategory(CharIDModel):
    """The categories of spam emails."""

    name = models.CharField(max_length=30)
    default = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name_plural = "spam categories"

    def __str__(self):
        return self.name


class ReplyTemplate(CharIDModel):
    """Custom reply templates."""

    body = models.TextField()
    category = models.ForeignKey(
        SpamCategory, default=get_default_category, on_delete=models.CASCADE
    )

    @property
    def snippet(self):
        """Get the first few characters of the reply."""
        return self.body[:40]

    def __str__(self):
        return self.snippet


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
                # There may not be an included in-reply-to header, check the
                # email address.
                conversation = Conversation.objects.filter(
                    sender_email=message.recipient_email
                ).first()
                if not conversation:
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
    reporter_email = models.CharField(max_length=1000, blank=True, db_index=True)

    # The name of our sender (the bot).
    sender_name = models.CharField(max_length=1000, default=generate_fake_name)

    # The email address of the bot (so we can match incoming messages).
    sender_email = models.CharField(max_length=1000, blank=True, db_index=True)

    # The secret key for editing the conversation.
    secret_key = models.CharField(max_length=1000, default=generate_key)

    # The fake domain to use to send mail from.
    domain = models.ForeignKey(
        Domain, default=get_random_domain, on_delete=models.CASCADE
    )

    # The category of the email (sales, scam, dating, etc).
    category = models.ForeignKey(
        SpamCategory, default=get_default_category, on_delete=models.CASCADE
    )

    # Whether this has been classified by a trusted human.
    classified = models.BooleanField(default=False, db_index=True)

    # When the conversation was created.
    created = models.DateTimeField(auto_now_add=True)

    objects = ConversationManager()

    def __str__(self):
        return "%s <%s>" % (self.sender_name, self.sender_email)

    def get_absolute_url(self):
        return reverse("main:conversation-view", args=[self.id])

    @property
    def messages(self):
        """
        Return a QuerySet of all the messages in the converation.

        The QuerySet is sorted by ascending date, ie the most recent items are
        last.
        """
        return self.message_set.all().order_by("timestamp")

    @property
    def calculated_sender_username(self):
        """Derive a username from the sender's name."""
        split_name = self.sender_name.split()
        return (split_name[0][0] + split_name[1]).lower()

    @property
    def calculated_sender_email(self):
        """Derive a username from the sender's username."""
        return "%s@%s" % (self.calculated_sender_username, self.domain.name)

    def save(self, *args, **kwargs):
        """Generate the sender_email on saving."""
        if not self.sender_email:
            self.sender_email = self.calculated_sender_email

        super().save(*args, **kwargs)


class MessageManager(models.Manager):
    def unsent(self):
        return Message.objects.exclude(send_on=None).filter(
            send_on__lt=datetime.datetime.now()
        )


class Message(CharIDModel):
    """A single email message."""

    DIRECTIONS = [("F", "Forwarded"), ("S", "Sent"), ("R", "Received")]

    timestamp = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    # Whether this email was forwarded to us, sent by us, or received by us from
    # the spammer.
    direction = models.CharField(choices=DIRECTIONS, max_length=10)

    sender = models.CharField(max_length=1000, blank=True)
    recipient = models.CharField(max_length=1000, blank=True)
    subject = models.CharField(max_length=1000)

    # The email address of the person who forwarded the mail to us.
    forwarder = models.CharField(max_length=1000, blank=True)

    # The time to send the email on.
    send_on = models.DateTimeField(blank=True, null=True)

    # The plaintext body of the email.
    body = models.TextField()

    # Any quoted text we need to include in the message.
    quoted_text = models.TextField(blank=True)

    # The stripped body of the email (no signature).
    stripped_body = models.TextField(blank=True)

    # The message ID, so we can keep track of the conversation.
    message_id = models.CharField(max_length=1000, unique=True)

    # The in-reply-to header, which complements the ID.
    in_reply_to = models.CharField(max_length=1000, blank=True)

    objects = MessageManager()

    class Meta:
        ordering = ["timestamp"]
        indexes = [models.Index(fields=["timestamp", "conversation", "direction"])]

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse("main:conversation-view", args=[self.conversation.id])

    @property
    def sender_name(self):
        """Parse and return the sender's name."""
        if not self.sender:
            return ""
        return parse_email_address(self.sender)[0]

    @property
    def sender_email(self):
        """Parse and return the sender's email address."""
        if not self.sender:
            return ""
        return parse_email_address(self.sender)[1]

    @property
    def recipient_name(self):
        """Parse and return the recipient's name."""
        if not self.recipient:
            return ""
        return parse_email_address(self.recipient)[0]

    @property
    def recipient_email(self):
        """Parse and return the recipient's email address."""
        if not self.recipient:
            return ""
        return parse_email_address(self.recipient)[1]

    @property
    def best_body(self):
        """Return the best body to use (i.e. stripped_body if available)."""
        return self.stripped_body or self.body

    @classmethod
    def parse_from_webhook(cls, posted, forwarded=False):
        """Parse a message from the webhook and return a Message instance."""
        # Delete old messages with this ID, as it probably means the server
        # crashed on them and we need to redo whatever we did.
        cls.objects.filter(message_id=posted["id"]).delete()

        # Some mail is base64-encoded and the server doesn't handle that for us.
        html_body = try_decoding_base64(posted.get("body[html]", ""))
        text_body = try_decoding_base64(posted.get("body[text]", ""))
        message = cls()
        message.direction = "F" if forwarded else "R"
        message.sender = posted["addresses[from]"].replace("\n", " ")
        message.recipient = get_relevant_recipient(
            posted.get("addresses[to]", "").replace("\n", " ")
        )
        message.subject = re.sub(r"[\n\r]", " ", posted.get("subject", ""))
        message.body = text_body
        message.stripped_body = strip_html(html_body)
        message.message_id = posted["id"]
        message.in_reply_to = posted.get("in-reply-to", "")

        if not message.recipient or not message.body:
            return None

        if is_blacklisted(message):
            return None

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
            body = message.best_body
            sender, body = parse_forwarded_message(body)
            if (
                not sender
                or "@" not in sender
                or Domain.objects.filter(name=sender.split("@")[1].lower()).exists()
            ):
                # We couldn't locate a sender, or the sender is us, so abort.
                return None
            message.forwarder = message.sender
            message.sender = sender
            message.body = body
            message.stripped_body = ""

            # Strip Fw/Fwd from the subject.
            match = re.match(r"\W*Fwd?: (.*)$", message.subject, re.I)
            if match:
                message.subject = match.group(1)

            message.conversation = Conversation.objects.create(
                reporter_email=posted["addresses[from]"]
            )
        else:
            if (
                not message.sender
                or "@" not in message.sender_email
                or Domain.objects.filter(
                    name=message.sender_email.split("@")[1].lower()
                ).exists()
            ):
                # We couldn't locate a sender, or the sender is us, so abort.
                return None

        message.save()

        return message

    def queue(self):
        """Queue the message for sending with a random delay, for realism."""
        if settings.DEBUG:
            send_on = datetime.datetime.now()
        else:
            send_on = datetime.datetime.now() + datetime.timedelta(
                seconds=random.randrange(60, 12 * 60 * 60)
            )
        self.timestamp = send_on
        self.send_on = send_on
        self.save()

    @classmethod
    def send_unsent(cls):
        """Send all ready unsent messages."""
        sent_count = 0
        for message in cls.objects.unsent():
            message.send()
            sent_count += 1
        return sent_count

    def send(self):
        """Send the message through email."""
        conversation = self.conversation

        body = self.body

        if self.quoted_text:
            body += "\n\n" + self.quoted_text

        email = EmailMessage(
            self.subject,
            body + "\n\n\n\n",
            "%s <%s>" % (conversation.sender_name, self.conversation.sender_email),
            [self.recipient],
            headers={"Message-ID": self.message_id},
        )

        email.send(fail_silently=True)

        self.send_on = None
        self.save()

    def get_random_reply(self):
        """Get a random reply to this message, based on its contents."""
        # Right now it's not very much based on the original email's contents.
        reply = (
            ReplyTemplate.objects.filter(category=self.conversation.category)
            .order_by("?")
            .first()
        )
        return spintax.spin(reply.body)

    def save(self, *args, **kwargs):
        """Generate a message ID on saving."""
        if not self.conversation_id:
            # In order to get_by_message, we need to already have set in_reply_to.
            self.conversation = Conversation.objects.get_by_message(self)

        if not self.message_id:
            self.message_id = generate_message_id(self.conversation.domain.name)

        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            # This means this message is a duplicate.
            pass
