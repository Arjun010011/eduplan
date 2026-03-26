import os
import django
from django.test import Client
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduplan.settings')
django.setup()

c = Client()
response = c.post('/api/planner/generate/', {
    'teacher_name': 'Test',
    'board': 'CBSE',
    'grade': 10,
    'subject': 'Math',
    'num_lessons': 5
}, content_type='application/json')

print("Status:", response.status_code)
print("Content:", response.content)
