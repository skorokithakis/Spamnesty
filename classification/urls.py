from classification.views import classify, delete_conversation
from django.conf.urls import url

urlpatterns = [
    url(r'^classify/$', classify, name="classify"),
    url(r'^delete/$', delete_conversation, name="delete"),
]
