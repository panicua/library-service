from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("user.urls", namespace="users")),
    path("api/books/", include("books_app.urls", namespace="books_app")),
    path("api/payments/", include("payment_app.urls", namespace="payment")),
    path(
        "api/borrowings/",
        include("borrowing_app.urls", namespace="borrowing_app"),
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
]
