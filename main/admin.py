from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin

from .models import Conversation
from .models import Domain
from .models import Message
from .models import ReplyTemplate
from .models import SpamCategory


@admin.register(SpamCategory)
class SpamCategoryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["name", "default"]
    search_fields = ["name"]


@admin.register(ReplyTemplate)
class ReplyTemplateAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["id", "snippet", "category"]
    search_fields = ["body"]
    list_filter = ["category"]


@admin.register(Domain)
class DomainAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["name", "company_name"]
    search_fields = ["name", "company_name"]


class MessageInline(DjangoQLSearchMixin, admin.TabularInline):
    model = Message
    fields = ["sender", "recipient", "body"]


@admin.register(Conversation)
class ConversationAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "sender_name",
        "sender_email",
        "domain",
        "category",
        "created",
    ]
    search_fields = ["id", "sender_email", "sender_name"]
    list_filter = ["category"]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    raw_id_fields = ("conversation",)
    list_display = [
        "conversation",
        "recipient",
        "subject",
        "timestamp",
        "direction",
        "send_on",
    ]
    search_fields = ["recipient", "subject", "message_id"]
