import json
import re
import os
import tempfile

from django.core.files import File
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _require(obj, key, context):
    if key not in obj:
        raise RuntimeError(f"Missing '{key}' in {context}.")
    return obj[key]


def compile_plan_json_to_pdf(plan_json_text, plan_id):
    """
    Renders a PDF using ReportLab from a JSON plan string.

    Returns:
        (pdf_django_file, pdf_filename) on success
        Raises RuntimeError on failure.
    """
    plan_json_text = plan_json_text.strip()
    if plan_json_text.startswith("```"):
        lines = plan_json_text.splitlines()
        plan_json_text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    # Extract the first JSON object if extra text sneaks in.
    if "{" in plan_json_text and "}" in plan_json_text:
        start = plan_json_text.find("{")
        end = plan_json_text.rfind("}")
        plan_json_text = plan_json_text[start:end + 1]

    # Remove common trailing commas that break strict JSON.
    plan_json_text = re.sub(r",(\s*[}\]])", r"\1", plan_json_text)

    try:
        plan = json.loads(plan_json_text)
    except json.JSONDecodeError as exc:
        hint = ""
        if not plan_json_text.rstrip().endswith("}"):
            hint = " Output looks truncated. Reduce verbosity or increase model max_output_tokens."
        raise RuntimeError(f"Invalid plan JSON: {exc}.{hint}")

    title = _require(plan, "title", "plan")
    teacher_name = _require(plan, "teacher_name", "plan")
    board = _require(plan, "board", "plan")
    grade = _require(plan, "grade", "plan")
    subject = _require(plan, "subject", "plan")
    date_range = _require(plan, "date_range", "plan")
    weeks = _require(plan, "weeks", "plan")

    if not isinstance(weeks, list) or not weeks:
        raise RuntimeError("Plan JSON 'weeks' must be a non-empty list.")

    work_dir = tempfile.mkdtemp()
    pdf_filename = f"plan_{plan_id}.pdf"
    pdf_path = os.path.join(work_dir, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=title,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Teacher Name: {teacher_name}", styles["Normal"]))
    story.append(Paragraph(f"Board: {board}", styles["Normal"]))
    story.append(Paragraph(f"Grade: {grade}", styles["Normal"]))
    story.append(Paragraph(f"Subject: {subject}", styles["Normal"]))
    story.append(Paragraph(f"Date Range: {date_range}", styles["Normal"]))
    story.append(Spacer(1, 18))

    table_header = [
        "Week No.",
        "Dates",
        "Chapter / Topic",
        "Learning Objectives",
        "Activities",
        "Status",
    ]
    table_rows = [table_header]

    for week in weeks:
        week_no = _require(week, "week_no", "week")
        week_dates = _require(week, "date_range", "week")
        topic = _require(week, "topic", "week")
        objectives = _require(week, "objectives", "week")
        activities = _require(week, "activities", "week")

        if not isinstance(objectives, list) or not isinstance(activities, list):
            raise RuntimeError("Week 'objectives' and 'activities' must be arrays.")

        objectives_text = "<br/>".join([str(item) for item in objectives])
        activities_text = "<br/>".join([str(item) for item in activities])

        table_rows.append(
            [
                str(week_no),
                str(week_dates),
                str(topic),
                Paragraph(objectives_text, styles["Normal"]),
                Paragraph(activities_text, styles["Normal"]),
                "[ ]",
            ]
        )

    table = Table(table_rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    for row_idx in range(1, len(table_rows)):
        if row_idx % 2 == 1:
            table.setStyle(
                TableStyle([("BACKGROUND", (0, row_idx), (-1, row_idx), colors.whitesmoke)])
            )

    story.append(table)

    doc.build(story)

    pdf_file = open(pdf_path, "rb")
    return File(pdf_file), pdf_filename
