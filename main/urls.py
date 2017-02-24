"""The main application's URLs."""

from django.conf.urls import url

from main.views import generic, learn, webhooks


urlpatterns = [
    url(r'^$', generic.home, name="home"),
    url(r'^conversations/(?P<conversation_id>[^/]*)/$', generic.conversation_view, name="conversation-view"),
    url(r'^conversations/(?P<conversation_id>[^/]*)/delete/$', generic.conversation_delete, name="conversation-delete"),
    url(r'^conversations/(?P<conversation_id>[^/]*)/change/$', generic.conversation_change, name="conversation-change"),
]

urlpatterns += [
    url(r'^webhooks/forwarded/$', webhooks.forwarded, name="forwarded-webhook"),
    url(r'^webhooks/email/$', webhooks.email, name="email-webhook"),
    url(r'^webhooks/cron/$', webhooks.cron, name="cron-webhook"),
]

urlpatterns += [
    url(r'^entrary/misc/export-messages/$', learn.export_messages, name="learn-export-messages"),
]
