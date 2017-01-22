from classification.views import classify
from django.conf.urls import url

urlpatterns = [
    url(r'^classify/$', classify, name="classify"),
]
