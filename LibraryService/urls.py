from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/books/", include("books_app.urls", namespace="books_app")),
    path("api/payment/", include("payment_app.urls", namespace="payment")),
    path(
        "api/borrowings/",
        include("borrowing_app.urls", namespace="borrowing_app"),
    ),
]
