from django.shortcuts import render
from rest_framework import viewsets

from borrowing_app.models import Borrowing
from serializers import BorrowingSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

