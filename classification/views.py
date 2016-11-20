from annoying.decorators import render_to
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from main.models import Conversation, SpamCategory


@require_http_methods(["GET", "POST"])
@render_to("classify.html")
def classify(request):
    """
    Allow staff to classify conversations into categories.
    """
    if not request.user.is_staff:
        raise Http404

    if request.method == "POST":
        conversation = get_object_or_404(Conversation, pk=request.POST.get("conversation_id"))
        category = get_object_or_404(SpamCategory, pk=request.POST.get("category_id", ""))
        conversation.category = category
        conversation.classified = True
        conversation.save()
        return {"result": "success"}
    else:
        conversations = Conversation.objects.filter(classified=False)[:10]
        categories = SpamCategory.objects.all()
        return {"conversations": conversations, "spam_categories": categories}
