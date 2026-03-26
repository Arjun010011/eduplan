from django.db import models


class Textbook(models.Model):
    BOARD_CHOICES = [
        ('CBSE', 'CBSE'),
        ('ICSE', 'ICSE'),
        ('KA_STATE', 'Karnataka State Board'),
    ]

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    grade = models.IntegerField()
    board = models.CharField(max_length=20, choices=BOARD_CHOICES)
    language = models.CharField(max_length=50, default='English')
    file_url = models.URLField(max_length=500)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['board', 'grade', 'subject']

    def __str__(self):
        return f"{self.board} | Grade {self.grade} | {self.subject} — {self.title}"
