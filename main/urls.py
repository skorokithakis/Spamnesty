from django.conf.urls import url

from main.views import generic
from main.views import webhooks


urlpatterns = [
    url(r'^$', generic.home, name="home"),
    url(r'^conversations/(?P<conversation_id>.*)/$', generic.conversation_view, name="conversation-view"),
]

urlpatterns += [
    url(r'^webhooks/forwarded/$', webhooks.forwarded, name="forwarded-webhook"),
    url(r'^webhooks/email/$', webhooks.email, name="email-webhook"),
    url(r'^webhooks/cron/$', webhooks.cron, name="cron-webhook"),
]
