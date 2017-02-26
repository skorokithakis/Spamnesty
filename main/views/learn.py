"""ML-related views."""
import json

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.http import StreamingHttpResponse

from main.models import Conversation, SpamCategory


def message_exporter():
    # We need to do these contortions so we can stream the response.
    yield '{"categories": '
    yield json.dumps([{"id": cat.id, "name": cat.name} for cat in SpamCategory.objects.all()], indent=2) + ', "messages": ['

    for counter, conversation in enumerate(Conversation.objects.annotate(num_messages=Count("message")).filter(num_messages__gte=1)):
        yield "," if counter else ""
        message = conversation.messages[0]
        message_exp = {
            "message_id": message.message_id,
            "subject": message.subject,
            "body": message.best_body,
            "category": conversation.category_id,
            "classified": conversation.classified,
        }
        yield json.dumps(message_exp, indent=2, sort_keys=True)
    yield "]}"


@user_passes_test(lambda u: u.is_superuser)
def export_messages(request):
    """Export spam messages as a JSON object."""
    response = StreamingHttpResponse(message_exporter(), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="spamnesty_messages.json"'
    return response
