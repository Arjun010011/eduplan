from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CoursePlan
from .serializers import CoursePlanRequestSerializer, CoursePlanResponseSerializer
import json
from datetime import timedelta

from .utils.gemini_client import generate_week_details
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

    Accepts course plan parameters, calls Gemini to generate plan JSON,
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
            start_date=data['start_date'],
            end_date=data['end_date'],
            prompt_input=data.get('instructions', ''),
        )

        try:
            weeks = _build_week_ranges(data['start_date'], data['end_date'])
            all_weeks = []
            chunk_size = 10
            for i in range(0, len(weeks), chunk_size):
                chunk = weeks[i:i + chunk_size]
                chunk_details = generate_week_details(
                    teacher_name=data['teacher_name'],
                    board=data['board'],
                    grade=data['grade'],
                    subject=data['subject'],
                    start_date=str(data['start_date']),
                    end_date=str(data['end_date']),
                    instructions=data.get('instructions', ''),
                    week_chunk=chunk,
                )
                normalized = _normalize_week_chunk(chunk, chunk_details)
                all_weeks.extend(normalized)

            plan_payload = {
                "title": "Course Completion Plan",
                "teacher_name": data['teacher_name'],
                "board": data['board'],
                "grade": str(data['grade']),
                "subject": data['subject'],
                "date_range": f"{data['start_date']} to {data['end_date']}",
                "weeks": all_weeks,
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


def _build_week_ranges(start_date, end_date):
    weeks = []
    current = start_date
    week_no = 1
    while current <= end_date:
        week_end = min(current + timedelta(days=6), end_date)
        weeks.append(
            {
                "week_no": week_no,
                "date_range": f"{current.isoformat()} to {week_end.isoformat()}",
                "buffer": False,
            }
        )
        week_no += 1
        current = week_end + timedelta(days=1)

    for i in range(1, min(2, len(weeks)) + 1):
        weeks[-i]["buffer"] = True

    return weeks


def _normalize_week_chunk(chunk, chunk_details):
    if not isinstance(chunk_details, list):
        raise RuntimeError("Week details must be a JSON array.")

    by_week_no = {}
    for item in chunk_details:
        if not isinstance(item, dict):
            continue
        try:
            week_no = int(item.get("week_no"))
        except (TypeError, ValueError):
            continue
        by_week_no[week_no] = item

    normalized = []
    for week in chunk:
        item = by_week_no.get(week["week_no"], {})
        topic = str(item.get("topic", "")).strip()
        objectives = item.get("objectives") or []
        activities = item.get("activities") or []

        if not isinstance(objectives, list):
            objectives = [str(objectives)]
        if not isinstance(activities, list):
            activities = [str(activities)]

        objectives = [str(v).strip() for v in objectives if str(v).strip()][:2]
        activities = [str(v).strip() for v in activities if str(v).strip()][:2]

        if week["buffer"]:
            topic = "Revision / Assessment"
            if not objectives:
                objectives = [
                    "Review key concepts covered so far.",
                    "Identify weak areas for focused practice.",
                ]
            if not activities:
                activities = [
                    "Revision worksheet and class discussion.",
                    "Short unit test or quiz.",
                ]

        if not topic:
            topic = "Syllabus Progression"
        if len(objectives) < 2:
            objectives += ["Reinforce key concepts."] * (2 - len(objectives))
        if len(activities) < 2:
            activities += ["Guided practice and discussion."] * (2 - len(activities))

        normalized.append(
            {
                "week_no": week["week_no"],
                "date_range": week["date_range"],
                "topic": topic,
                "objectives": objectives[:2],
                "activities": activities[:2],
            }
        )

    return normalized
