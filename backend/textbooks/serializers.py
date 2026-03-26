from rest_framework import serializers
from .models import Textbook


class TextbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Textbook
        fields = '__all__'
