from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import Message
from ..utils import construct_reply


@csrf_exempt
def forwarded(request):
    "The webhook that fires when a user forwards a legitimate email."
    message = Message.parse_from_mailgun(request.POST, forwarded=True)
    reply = construct_reply(message)
    reply.send()

    return HttpResponse("OK")


@csrf_exempt
def email(request):
    "The webhook that fires when we get some spam."
    message = Message.parse_from_mailgun(request.POST)
    reply = construct_reply(message)
    reply.send()

    return HttpResponse("OK")
