"""ML-related views."""
import json

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.http import HttpResponse

from main.models import Conversation, SpamCategory


@user_passes_test(lambda u: u.is_superuser)
def export_messages(request):
    """Export spam messages as json object."""
    categories = [{"id": cat.id, "name": cat.name} for cat in SpamCategory.objects.all()]
    messages = []
    for conversation in Conversation.objects.annotate(num_messages=Count("message")).filter(num_messages__gte=1):
        message = conversation.messages[0]
        message_exp = {
            "message_id": message.message_id,
            "subject": message.subject,
            "body": message.best_body,
            "category": conversation.category_id,
            "classified": conversation.classified,
        }
        messages.append(message_exp)

    exp = {"categories": categories, "messages": messages}
    j_str = json.dumps(exp, indent=2, sort_keys=True)
    response = HttpResponse(j_str, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="spamnesty_messages.json"'
    return response
