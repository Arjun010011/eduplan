from rest_framework import serializers
from .models import CoursePlan


class CoursePlanRequestSerializer(serializers.Serializer):
    teacher_name = serializers.CharField(max_length=150)
    board = serializers.ChoiceField(choices=['CBSE', 'ICSE', 'KA_STATE'])
    grade = serializers.IntegerField(min_value=1, max_value=12)
    subject = serializers.CharField(max_length=100)
    num_lessons = serializers.IntegerField(min_value=1, max_value=60)
    instructions = serializers.CharField(required=False, allow_blank=True, default='')


class CoursePlanResponseSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.pdf_file and request:
            return request.build_absolute_uri(obj.pdf_file.url)
        return None

    class Meta:
        model = CoursePlan
        fields = [
            'id', 'teacher_name', 'board', 'grade', 'subject',
            'num_lessons', 'latex_output', 'pdf_url', 'created_at'
        ]
