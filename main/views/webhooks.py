import json
import re

from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from raven.contrib.django.raven_compat.models import client

from ..models import Message
from ..utils import check_last_messages_similarity
from ..utils import construct_reply


def process_forwarded_email(request):
    """Perform necessary tasks when a user forwards a legitimate email."""
    from_addr = request.POST.get("addresses[from]")
    if not from_addr:
        return HttpResponse("Empty sender.")

    if Message.objects.filter(message_id=request.POST.get("id", "")).exists():
        # Ignore webhook retries if we've already added the message.
        return HttpResponse("OK")

    # Try to parse the forwarded message.
    try:
        message = Message.parse_from_webhook(request.POST, forwarded=True)
    except Exception:
        # Notify Sentry.
        client.captureException()
        message = None

    if not message:
        print(json.dumps(request.POST))
        # Notify the sender that we couldn't find the spammer's address.
        EmailMessage(
            subject=render_to_string(
                "emails/forward_no_email_subject.txt", request=request
            ).strip(),
            body=render_to_string("emails/forward_no_email_body.txt", request=request),
            to=[from_addr],
        ).send()
    else:
        # Notify the sender that we've received it.
        EmailMessage(
            subject=render_to_string(
                "emails/forward_received_subject.txt", request=request
            ).strip(),
            body=render_to_string(
                "emails/forward_received_body.txt",
                context={"message": message},
                request=request,
            ),
            to=[from_addr],
        ).send()

        # Reply to the spammer.
        reply = construct_reply(message)
        reply.send()


def process_spam(request):
    """Perform necessary tasks when we get some email."""
    # Parse the received message.
    message = Message.parse_from_webhook(request.POST)

    # If there is no unsent message in the queue, queue one.
    if (
        message
        and message.conversation.messages.count() <= 40
        and not check_last_messages_similarity(message.conversation)
        and not message.conversation.messages.exclude(send_on=None).exists()
    ):
        # Reply to the spammer.
        reply = construct_reply(message)
        reply.queue()


@csrf_exempt
def email(request):
    if "id" in request.POST:
        if re.search(
            r"spa?@mnesty\.com", request.POST.get("addresses[to]", "").lower()
        ):
            process_forwarded_email(request)
        else:
            process_spam(request)
    return HttpResponse("OK")


@csrf_exempt
def cron(request):
    """Send unsent emails."""
    Message.send_unsent()
    return HttpResponse("OK")
