from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CoursePlan
from .serializers import CoursePlanRequestSerializer, CoursePlanResponseSerializer
import json

from .utils.gemini_client import generate_lesson_details
from .utils.pdf_renderer import compile_plan_json_to_pdf


def _stringify_serializer_errors(errors):
    if isinstance(errors, dict):
        parts = []
        for field, messages in errors.items():
            if isinstance(messages, (list, tuple)) and messages:
                parts.append(f"{field}: {messages[0]}")
            else:
                parts.append(f"{field}: {messages}")
        return '; '.join(parts)
    if isinstance(errors, (list, tuple)) and errors:
        return str(errors[0])
    return str(errors)


class GenerateCoursePlanView(APIView):
    """
    POST /api/planner/generate/

    Accepts course plan parameters, calls the AI to generate lesson plan JSON,
    renders it to PDF, and returns the download URL.
    """

    def post(self, request):
        serializer = CoursePlanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            message = _stringify_serializer_errors(serializer.errors)
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        plan = CoursePlan.objects.create(
            teacher_name=data['teacher_name'],
            board=data['board'],
            grade=data['grade'],
            subject=data['subject'],
            num_lessons=data['num_lessons'],
            prompt_input=data.get('instructions', ''),
        )

        try:
            # Build a simple lesson list: [{"lesson_no": 1}, {"lesson_no": 2}, ...]
            lessons_input = [{"lesson_no": i + 1} for i in range(data['num_lessons'])]

            all_lessons = []
            chunk_size = 5  # Small chunks keep API responses well under token limits
            for i in range(0, len(lessons_input), chunk_size):
                chunk = lessons_input[i:i + chunk_size]
                chunk_details = generate_lesson_details(
                    teacher_name=data['teacher_name'],
                    board=data['board'],
                    grade=data['grade'],
                    subject=data['subject'],
                    instructions=data.get('instructions', ''),
                    lesson_chunk=chunk,
                )
                normalized = _normalize_lesson_chunk(chunk, chunk_details)
                all_lessons.extend(normalized)

            plan_payload = {
                "title": "Lesson Plan",
                "teacher_name": data['teacher_name'],
                "board": data['board'],
                "grade": str(data['grade']),
                "subject": data['subject'],
                "num_lessons": data['num_lessons'],
                "lessons": all_lessons,
            }
            plan_json_text = json.dumps(plan_payload, ensure_ascii=False, separators=(",", ":"))
        except Exception as e:
            plan.delete()
            return Response({'error': f"OpenRouter API error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

        plan.latex_output = plan_json_text
        plan.save()

        try:
            pdf_file, pdf_filename = compile_plan_json_to_pdf(plan_json_text, plan.id)
            plan.pdf_file.save(pdf_filename, pdf_file)
            pdf_file.close()
        except RuntimeError as e:
            return Response({'error': f"PDF compilation error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        plan.save()

        response_serializer = CoursePlanResponseSerializer(plan, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


def _normalize_lesson_chunk(chunk, chunk_details):
    if not isinstance(chunk_details, list):
        raise RuntimeError("Lesson details must be a JSON array.")

    by_lesson_no = {}
    for item in chunk_details:
        if not isinstance(item, dict):
            continue
        try:
            lesson_no = int(item.get("lesson_no"))
        except (TypeError, ValueError):
            continue
        by_lesson_no[lesson_no] = item

    normalized = []
    for lesson in chunk:
        item = by_lesson_no.get(lesson["lesson_no"], {})
        topic = str(item.get("topic", "")).strip()
        objectives = item.get("objectives") or []
        activities = item.get("activities") or []

        if not isinstance(objectives, list):
            objectives = [str(objectives)]
        if not isinstance(activities, list):
            activities = [str(activities)]

        objectives = [str(v).strip() for v in objectives if str(v).strip()]
        activities = [str(v).strip() for v in activities if str(v).strip()]

        if not topic:
            topic = "Syllabus Progression"
        if len(objectives) < 2:
            objectives += ["Understand core concepts."] * (2 - len(objectives))
        if len(activities) < 2:
            activities += ["Guided practice and review."] * (2 - len(activities))

        normalized.append(
            {
                "lesson_no": lesson["lesson_no"],
                "topic": topic,
                "objectives": objectives,
                "activities": activities,
            }
        )

    return normalized
