from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Textbook
from .serializers import TextbookSerializer


class TextbookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Textbook.objects.all()
    serializer_class = TextbookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['board', 'grade', 'subject', 'language']
    search_fields = ['title', 'subject']
