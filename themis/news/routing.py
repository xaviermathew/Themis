from rest_framework.routers import DefaultRouter

from themis.news import viewsets

router = DefaultRouter()
router.register(r'news/news', viewsets.NewsIndexViewSet)
