import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduplan.settings')
django.setup()
from planner.utils.pdf_renderer import compile_plan_json_to_pdf
import json

dummy_plan = {
    "title": "Lesson Plan",
    "teacher_name": "Test",
    "board": "CBSE",
    "grade": "10",
    "subject": "Math",
    "num_lessons": 5,
    "lessons": [
        {"lesson_no": 1, "topic": "Algebra", "objectives": ["Obj1", "Obj2"], "activities": ["Act1", "Act2"]}
    ]
}

try:
    pdf_file, pdf_filename = compile_plan_json_to_pdf(json.dumps(dummy_plan), 1)
    print("PDF File created:", pdf_filename)
except Exception as e:
    import traceback
    traceback.print_exc()
