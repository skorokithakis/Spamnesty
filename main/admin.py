from django.contrib import admin

from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "sender_name", "sender_email"]
    search_fields = ["sender_name", "sender_email"]
