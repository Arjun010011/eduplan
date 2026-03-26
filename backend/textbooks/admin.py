from django.contrib import admin
from .models import Textbook


@admin.register(Textbook)
class TextbookAdmin(admin.ModelAdmin):
    list_display = ('board', 'grade', 'subject', 'title', 'language')
    search_fields = ('title', 'subject')
    list_filter = ('board', 'grade', 'subject', 'language')
