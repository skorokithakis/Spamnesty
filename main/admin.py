from django.contrib import admin

from .models import Conversation, Domain, Message, ReplyTemplate, SpamCategory


@admin.register(SpamCategory)
class SpamCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "default"]
    search_fields = ["name"]


@admin.register(ReplyTemplate)
class ReplyTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "snippet", "category"]
    search_fields = ["body"]
    list_filter = ["category"]


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ["name", "company_name"]
    search_fields = ["name", "company_name"]


class MessageInline(admin.TabularInline):
    model = Message
    fields = ["sender", "recipient", "body"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "sender_name", "sender_email", "domain", "category"]
    search_fields = ["id", "sender_email", "sender_name"]
    list_filter = ["category"]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "recipient", "subject", "timestamp", "direction", "send_on"]
    search_fields = ["recipient", "subject", "message_id"]
