'''
 This view facilitates testing.
'''
import json

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse

from main.models import Conversation, SpamCategory


@user_passes_test(lambda u: u.is_superuser)
def export_spam(request):
    "Export spam messages as json object"

    categories = []
    for cat in SpamCategory.objects.all():
        cat_exp = {"id": cat.id, "name": cat.name}
        categories.append(cat_exp)
    msgs = []
    for conv in Conversation.objects.all():
        msg = conv.messages[0]
        msg_exp = {"message_id": msg.message_id, "subject": msg.subject, "body": msg.body,
                   "category": conv.category_id, "classified": conv.classified}
        msgs.append(msg_exp)
    exp = {"categories": categories, "messages": msgs}
    j_str = json.dumps(exp, indent=4, sort_keys=True)
    response = HttpResponse(j_str, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="spamnesty_msgs.json"'
    return response
