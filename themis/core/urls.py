import importlib
import logging
import re

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import re_path, path, include
from django.views.static import serve

from themis.core import views

_LOG = logging.getLogger(__name__)

api_urls = []
for app_label in settings.PROJECT_APPS:
    try:
        router = importlib.import_module('%s.routing' % app_label).router
    except ModuleNotFoundError as ex:
        _LOG.warning('error importing router for app:%s - %s' % (app_label, ex))
    else:
        api_urls.extend(router.urls)

urlpatterns = [
    url(r'^$', views.home),
    url(r'^admin/', admin.site.urls),
    re_path(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
            serve,
            kwargs={'document_root': settings.STATIC_ROOT}),
    path('api/v1/', include(api_urls)),
]
