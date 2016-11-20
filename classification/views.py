from annoying.decorators import render_to
from django.http import Http404

from main.models import Conversation, SpamCategory


@render_to("classify.html")
def classify(request):
    if not request.user.is_staff:
        raise Http404
    conversations = Conversation.objects.filter(classified=False)[:10]
    categories = SpamCategory.objects.all()
    return {"conversations": conversations, "categories": categories}
