from django.contrib import admin
from .models import CoursePlan


@admin.register(CoursePlan)
class CoursePlanAdmin(admin.ModelAdmin):
    list_display = ('teacher_name', 'board', 'grade', 'subject', 'start_date', 'end_date', 'created_at')
    search_fields = ('teacher_name', 'subject')
    list_filter = ('board', 'grade', 'subject')
