from annoying.decorators import render_to
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from main.models import Conversation, SpamCategory


@staff_member_required
@require_http_methods(["GET", "POST"])
@render_to("classify.html")
def classify(request):
    """Allow staff to classify conversations into categories."""
    if request.method == "POST":
        conversation = get_object_or_404(
            Conversation, pk=request.POST.get("conversation_id")
        )
        category = get_object_or_404(
            SpamCategory, pk=request.POST.get("category_id", "")
        )
        conversation.category = category
        conversation.classified = True
        conversation.save()
        return {"result": "success"}
    else:
        conversations = Conversation.objects.filter(classified=False)
        conv_count = Conversation.objects.count()
        progress = (
            int((100.0 * conversations.count()) / conv_count) if conv_count else 100
        )

        categories = SpamCategory.objects.all()
        return {
            "conversations": conversations[:10],
            "spam_categories": categories,
            "progress": 100 - progress,
        }


@staff_member_required
@require_http_methods(["POST"])
@render_to("classify.html")
def delete_conversation(request):
    """Allow staff to delete conversations."""
    conversation = get_object_or_404(
        Conversation, pk=request.POST.get("conversation_id")
    )
    conversation.delete()
    return {"result": "success"}
