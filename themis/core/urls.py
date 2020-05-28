import re

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import re_path
from django.views.static import serve

from themis.core import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    re_path(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
            serve,
            kwargs={'document_root': settings.STATIC_ROOT}),
    url(r'^$', views.home),
]
