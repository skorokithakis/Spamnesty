import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import Message
from ..utils import construct_reply


@csrf_exempt
def forwarded(request):
    "The webhook that fires when a user forwards a legitimate email."
    message = Message.parse_from_mailgun(request.POST, forwarded=True)
    reply = construct_reply(message)
    reply.queue()

    return HttpResponse("OK")


@csrf_exempt
def email(request):
    "The webhook that fires when we get some spam."
    message = Message.parse_from_mailgun(request.POST)
    reply = construct_reply(message)
    reply.queue()

    return HttpResponse("OK")


@csrf_exempt
def cron(request):
    "The webhook that is called when it's time to send emails."
    unsent_messages = Message.objects.exclude(send_on=None).filter(send_on__lt=datetime.datetime.now())
    for message in unsent_messages:
        print("sending message")
        message.send()

    return HttpResponse("OK")
