from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from rest_framework import viewsets

from books_app.models import Book
from books_app.permissions import IsAdminOrReadOnly
from books_app.serializers import BookSerializer, BookListSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of books",
        description="Retrieve a list of all books. Accessible by anyone.",
        responses={200: BookListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Retrieve a single book",
        description="Retrieve the details of a specific book by its ID. Accessible by anyone.",
        responses={200: BookSerializer}
    ),
    create=extend_schema(
        summary="Create a new book",
        description="Create a new book. Accessible only by admin users.",
        responses={201: BookSerializer}
    ),
    update=extend_schema(
        summary="Update an existing book",
        description="Update the details of an existing book. Accessible only by admin users.",
        responses={200: BookSerializer}
    ),
    partial_update=extend_schema(
        summary="Partially update an existing book",
        description="Partially update the details of an existing book. Accessible only by admin users.",
        responses={200: BookSerializer}
    ),
    destroy=extend_schema(
        summary="Delete a book",
        description="Delete a specific book by its ID. Accessible only by admin users.",
        responses={204: OpenApiResponse(description="No Content")}
    )
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        return BookSerializer
