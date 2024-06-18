from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import viewsets
from books_app.models import Book
from books_app.serializers import BookSerializer, BookListSerializer
from books_app.permissions import IsAdminOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        responses={200: BookListSerializer(many=True)},
        description="Endpoint for listing all books",
        examples=[
            OpenApiExample(
                "Books List Example",
                summary="Example of a list of books",
                value=[
                    {
                        "id": 1,
                        "title": "Example Book Title",
                        "author": "Author Name",
                        "inventory": 5,
                        "daily_fee": "1.99",
                    },
                    {
                        "id": 2,
                        "title": "Another Book Title",
                        "author": "Another Author",
                        "inventory": 3,
                        "daily_fee": "2.50",
                    },
                ],
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        """Endpoint for listing all books"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=BookSerializer,
        responses={201: BookSerializer},
        description="Endpoint for creating a new book",
        examples=[
            OpenApiExample(
                "Create Book Example",
                summary="Example of creating a new book",
                value={
                    "title": "New Book Title",
                    "author": "New Author",
                    "cover": "HARD",
                    "inventory": 10,
                    "daily_fee": "3.00",
                },
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        """Endpoint for creating a new book"""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={200: BookSerializer},
        description="Endpoint for retrieving a book by ID",
        examples=[
            OpenApiExample(
                "Retrieve Book Example",
                summary="Example of retrieving a book by ID",
                value={
                    "id": 1,
                    "title": "Example Book Title",
                    "author": "Author Name",
                    "cover": "SOFT",
                    "inventory": 5,
                    "daily_fee": "1.99",
                },
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        """Endpoint for retrieving a book by ID"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        request=BookSerializer,
        responses={200: BookSerializer},
        description="Endpoint for updating a book by ID",
        examples=[
            OpenApiExample(
                "Update Book Example",
                summary="Example of updating a book",
                value={
                    "title": "Updated Book Title",
                    "author": "Updated Author",
                    "cover": "HARD",
                    "inventory": 8,
                    "daily_fee": "2.50",
                },
            )
        ],
    )
    def update(self, request, *args, **kwargs):
        """Endpoint for updating a book by ID"""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=BookSerializer,
        responses={200: BookSerializer},
        description="Endpoint for partially updating a book by ID",
        examples=[
            OpenApiExample(
                "Partial Update Book Example",
                summary="Example of partially updating a book",
                value={"title": "Partially Updated Book Title"},
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        """Endpoint for partially updating a book by ID"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={204: None},
        description="Endpoint for deleting a book by ID",
        examples=[
            OpenApiExample(
                "Delete Book Example", summary="Example of deleting a book", value=None
            )
        ],
    )
    def destroy(self, request, *args, **kwargs):
        """Endpoint for deleting a book by ID"""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer
