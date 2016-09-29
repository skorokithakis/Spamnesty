from django.contrib import admin

from .models import Domain, Conversation, Message


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ["name", "company_name"]
    search_fields = ["name", "company_name"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "sender_name", "domain"]
    search_fields = ["id", "profile"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "recipient", "subject", "timestamp", "send_on"]
    search_fields = ["recipient", "subject", "message_id"]
