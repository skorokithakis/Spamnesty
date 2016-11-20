from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^entrary/', admin.site.urls),
    url(r'^', include('main.urls', namespace="main")),
    url(r'^', include('classification.urls', namespace="classification")),
]
