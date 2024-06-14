from rest_framework import viewsets

from borrowing_app.models import Borrowing
from borrowing_app.serializers import BorrowingSerializer, BorrowingListSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return BorrowingListSerializer
        return BorrowingSerializer

