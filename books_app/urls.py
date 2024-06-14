from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books_app.views import BookViewSet

router = DefaultRouter()
router.register("", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "books_app"
