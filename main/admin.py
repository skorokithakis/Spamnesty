from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id"]
    search_fields = ["id", "profile"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "recipient", "subject", "timestamp"]
    search_fields = ["recipient", "subject", "message_id"]
