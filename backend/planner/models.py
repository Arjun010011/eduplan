from django.db import models


class CoursePlan(models.Model):
    BOARD_CHOICES = [
        ('CBSE', 'CBSE'),
        ('ICSE', 'ICSE'),
        ('KA_STATE', 'Karnataka State Board'),
    ]

    teacher_name = models.CharField(max_length=150)
    board = models.CharField(max_length=20, choices=BOARD_CHOICES)
    grade = models.IntegerField()
    subject = models.CharField(max_length=100)
    num_lessons = models.IntegerField(default=20)
    prompt_input = models.TextField()
    latex_output = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='plans/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher_name} | {self.board} Grade {self.grade} {self.subject}"
