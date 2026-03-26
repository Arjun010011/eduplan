import json
import re
import os
import tempfile
from datetime import datetime

from django.core.files import File
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER


def _require(obj, key, context):
    if key not in obj:
        raise RuntimeError(f"Missing '{key}' in {context}.")
    return obj[key]


def compile_plan_json_to_pdf(plan_json_text, plan_id):
    plan_json_text = plan_json_text.strip()
    if plan_json_text.startswith("```"):
        lines = plan_json_text.splitlines()
        plan_json_text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    if "{" in plan_json_text and "}" in plan_json_text:
        start = plan_json_text.find("{")
        end = plan_json_text.rfind("}")
        plan_json_text = plan_json_text[start:end + 1]

    plan_json_text = re.sub(r",(\s*[}\]])", r"\1", plan_json_text)

    try:
        plan = json.loads(plan_json_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid plan JSON: {exc}.")

    title = _require(plan, "title", "plan")
    teacher_name = _require(plan, "teacher_name", "plan")
    board = _require(plan, "board", "plan")
    grade = _require(plan, "grade", "plan")
    subject = _require(plan, "subject", "plan")
    num_lessons = plan.get("num_lessons", "")
    lessons = _require(plan, "lessons", "plan")

    if not isinstance(lessons, list) or not lessons:
        raise RuntimeError("Plan JSON 'lessons' must be a non-empty list.")

    work_dir = tempfile.mkdtemp()
    pdf_filename = f"plan_{plan_id}.pdf"
    pdf_path = os.path.join(work_dir, pdf_filename)

    # 1.5 cm margins give 18 cm available width on A4 (21cm)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=title,
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        "ModernTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    metadata_style = ParagraphStyle(
        "Metadata",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#334155"),
        leading=14
    )
    
    table_text_style = ParagraphStyle(
        "TableText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # Title
    story.append(Paragraph(title, title_style))
    
    # Metadata Block
    date_str = datetime.now().strftime("%B %d, %Y")
    metadata_html = f"""
    <b>Teacher:</b> {teacher_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>Board:</b> {board} <br/>
    <b>Subject:</b> {subject} &nbsp;&nbsp;&nbsp;&nbsp; <b>Grade:</b> {grade} <br/>
    <b>Total Lessons:</b> {num_lessons} &nbsp;&nbsp;&nbsp;&nbsp; <b>Date Generated:</b> {date_str}
    """
    story.append(Paragraph(metadata_html, metadata_style))
    story.append(Spacer(1, 20))

    # Table Header
    table_header = [
        "No.",
        "Chapter / Topic",
        "Learning Objectives",
        "Activities / Resources",
        "Status",
    ]
    table_rows = [table_header]

    for lesson in lessons:
        lesson_no = _require(lesson, "lesson_no", "lesson")
        topic = _require(lesson, "topic", "lesson")
        objectives = _require(lesson, "objectives", "lesson")
        activities = _require(lesson, "activities", "lesson")

        if not isinstance(objectives, list) or not isinstance(activities, list):
            raise RuntimeError("Lesson 'objectives' and 'activities' must be arrays.")

        # Creating bulleted HTML strings
        obj_bullets = "".join([f"&bull; {item}<br/>" for item in objectives if str(item).strip()])
        act_bullets = "".join([f"&bull; {item}<br/>" for item in activities if str(item).strip()])

        table_rows.append(
            [
                str(lesson_no),
                Paragraph(str(topic), table_text_style),
                Paragraph(obj_bullets, table_text_style),
                Paragraph(act_bullets, table_text_style),
                "", # Empty status box for printing
            ]
        )

    # Column Widths sum to 18 cm
    # No (1 cm) | Topic (4 cm) | Objectives (6 cm) | Activities (5.5 cm) | Status (1.5 cm)
    col_widths = [1*cm, 4*cm, 6*cm, 5.5*cm, 1.5*cm]
    table = Table(table_rows, repeatRows=1, colWidths=col_widths)
    
    # Modern Table Styling
    table_style = TableStyle(
        [
            # Header Row Styling
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 12),
            
            # Global Cell Styling
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("ALIGN", (0, 1), (0, -1), "CENTER"), # Center the Lesson No
            ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
            ("TOPPADDING", (0, 1), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            
            # Grid and Borders
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ]
    )
    
    # Alternating Row Colors for Data Rows
    for row_idx in range(1, len(table_rows)):
        if row_idx % 2 == 1:
            table_style.add("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#f8fafc"))
        else:
            table_style.add("BACKGROUND", (0, row_idx), (-1, row_idx), colors.white)

    table.setStyle(table_style)
    story.append(table)
    doc.build(story)

    pdf_file = open(pdf_path, "rb")
    return File(pdf_file), pdf_filename
