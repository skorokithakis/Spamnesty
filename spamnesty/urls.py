from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r"^entrary/", admin.site.urls),
    url(r"^", include("main.urls", namespace="main")),
    url(r"^", include("classification.urls", namespace="classification")),
]


def handler500(request):
    from django.template import loader
    from django.http import HttpResponseServerError

    content_type = request.META.get(
        "HTTP_ACCEPT", request.META.get("CONTENT_TYPE", "text/html")
    ).lower()
    if content_type == "application/json":
        return HttpResponseServerError(
            '{"result": "error", "error_msg": "There was a server error. Please try again later."}',
            content_type="application/json",
        )

    t = loader.get_template("500.html")
    return HttpResponseServerError(t.render(context={}, request=request))
