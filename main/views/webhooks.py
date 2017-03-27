import datetime

from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from raven.contrib.django.raven_compat.models import client

from ..models import Message
from ..utils import construct_reply


@csrf_exempt
def forwarded(request):
    "The webhook that fires when a user forwards a legitimate email."

    if not request.POST.get("From"):
        return HttpResponse("Empty sender.")

    if Message.objects.filter(message_id=request.POST.get("Message-Id", "")).exists():
        # Ignore Mailgun retries if we've already added the message.
        return HttpResponse("OK")

    # Try to parse the forwarded message.
    try:
        message = Message.parse_from_mailgun(request.POST, forwarded=True)
    except:
        # Notify Sentry.
        client.captureException()
        message = None

    if not message:
        # Notify the sender that we couldn't find the spammer's address.
        EmailMessage(
            subject=render_to_string(
                "emails/forward_no_email_subject.txt",
                request=request
            ).strip(),
            body=render_to_string(
                "emails/forward_no_email_body.txt",
                request=request
            ),
            to=[request.POST["From"]],
        ).send()
    else:
        # Notify the sender that we've received it.
        EmailMessage(
            subject=render_to_string(
                "emails/forward_received_subject.txt",
                request=request
            ).strip(),
            body=render_to_string(
                "emails/forward_received_body.txt",
                context={"message": message},
                request=request
            ),
            to=[request.POST["From"]],
        ).send()

        # Reply to the spammer.
        reply = construct_reply(message)
        reply.send()

    return HttpResponse("OK")


@csrf_exempt
def email(request):
    "The webhook that fires when we get some spam."

    # Parse the received message.
    message = Message.parse_from_mailgun(request.POST)

    # If there is no unsent message in the queue, queue one.
    if (message and
       message.conversation.messages.count() <= 40 and
       not message.conversation.messages.exclude(send_on=None).exists()):
        # Reply to the spammer.
        reply = construct_reply(message)
        reply.queue()

    return HttpResponse("OK")


@csrf_exempt
def cron(request):
    "The webhook that is called when it's time to send emails."
    unsent_messages = Message.objects.exclude(send_on=None).filter(send_on__lt=datetime.datetime.now())
    for message in unsent_messages:
        message.send()

    return HttpResponse("OK")
