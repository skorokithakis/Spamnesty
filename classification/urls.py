from django.conf.urls import url

from classification.views import classify

urlpatterns = [
    url(r'^classify/$', classify, name="classify"),
]
