from django.conf.urls import url

from .views import classify
from .views import delete_conversation

app_name = "classification"
urlpatterns = [
    url(r"^classify/$", classify, name="classify"),
    url(r"^delete/$", delete_conversation, name="delete"),
]
