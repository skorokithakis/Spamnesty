from annoying.decorators import render_to
from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import constant_time_compare
from django.views.decorators.http import require_POST

from ..models import Conversation, SpamCategory


@render_to("home.html")
def home(request):
    if not (request.get_host().startswith("spa.") or settings.DEBUG):
        return {"TEMPLATE": "fake.html"}
    conversations = Conversation.objects.annotate(
            last_message_time=Max('message__timestamp'),
            num_messages=Count("message"),
        ).filter(num_messages__gt=11).order_by('-last_message_time')
    return {"conversations": conversations}


@require_POST
def conversation_delete(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    if constant_time_compare(request.GET.get("key"), conversation.secret_key) or request.user.is_staff:
        messages.success(request, "The conversation has been deleted.")
        conversation.delete()
    else:
        messages.error(request, "The conversation's secret key was invalid.")
    return redirect("main:home")


def conversation_change(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    category = get_object_or_404(SpamCategory, pk=request.GET.get("category", ""))
    if constant_time_compare(request.GET.get("key"), conversation.secret_key) or request.user.is_staff:
        messages.success(request, "The conversation's category has been changed.")
        conversation.category = category
        conversation.classified = request.user.is_staff
        conversation.save()
    else:
        messages.error(request, "The conversation's secret key was invalid.")
    return redirect(conversation)


@render_to("conversation_view.html")
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    own_conversation = constant_time_compare(request.GET.get("key"), conversation.secret_key)

    if own_conversation and "@" in conversation.reporter_email:
        other_conversations = Conversation.objects.filter(reporter_email=conversation.reporter_email)
    else:
        other_conversations = []

    # Sort with the default category being last.
    categories = SpamCategory.objects.order_by("default", "name")
    return {
        "conversation": conversation,
        "own": own_conversation,
        "spam_categories": categories,
        "other_conversations": other_conversations,
    }
