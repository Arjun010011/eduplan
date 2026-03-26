import json
import os
import re
import tempfile

import requests
from django.conf import settings

WEEK_CHUNK_PROMPT_TEMPLATE = """
You are an expert curriculum designer for Indian school boards.

Generate detailed weekly plan content in JSON for the following:
- Board: {board}
- Grade: {grade}
- Subject: {subject}
- Start Date: {start_date}
- End Date: {end_date}
- Teacher Name: {teacher_name}
- Special Instructions: {instructions}

Requirements:
- Use the standard {board} syllabus structure for Grade {grade} {subject}.
- Assume approximately 5 teaching days per week (Monday to Friday).
- For buffer weeks, set topic to "Revision / Assessment" and focus on review and testing.

Input weeks (JSON array). Each item includes week_no, date_range, and buffer:
{weeks_json}

Output ONLY a JSON array with the same number of items and same order.
Each item must include:
{{"week_no":1,"date_range":"YYYY-MM-DD to YYYY-MM-DD","topic":"...","objectives":["...","..."],"activities":["...","..."]}}

Rules:
- "objectives" and "activities" must be arrays with exactly 2 short strings.
- Keep each string concise (8-12 words max).
- Use compact JSON (no pretty formatting or extra whitespace).
- Do NOT include markdown fences or commentary. Return only JSON.
""".strip()


def _extract_json_array(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    if "[" in text and "]" in text:
        start = text.find("[")
        end = text.rfind("]")
        text = text[start:end + 1]
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    # Balance brackets/braces if the model truncates near the end.
    open_brackets = text.count("[")
    close_brackets = text.count("]")
    if open_brackets > close_brackets:
        text = text + ("]" * (open_brackets - close_brackets))
    open_braces = text.count("{")
    close_braces = text.count("}")
    if open_braces > close_braces:
        text = text + ("}" * (open_braces - close_braces))

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Heuristic repairs for missing commas.
        repaired = text
        repaired = re.sub(r"}\s*{", "},{", repaired)
        repaired = re.sub(r"\"\s*(?=[A-Za-z_][A-Za-z0-9_]*\"\s*:)", "\",", repaired)
        repaired = re.sub(r"\]\s*(?=[A-Za-z_][A-Za-z0-9_]*\"\s*:)", "],", repaired)
        repaired = re.sub(r"}\s*(?=[A-Za-z_][A-Za-z0-9_]*\"\s*:)", "},", repaired)
        return json.loads(repaired)


def generate_week_details(teacher_name, board, grade, subject, start_date, end_date, instructions, week_chunk):
    """
    Calls OpenRouter with a structured curriculum prompt.
    Returns a list of week dicts with topic/objectives/activities.
    """
    weeks_json = json.dumps(week_chunk, ensure_ascii=False, separators=(",", ":"))

    prompt = WEEK_CHUNK_PROMPT_TEMPLATE.format(
        teacher_name=teacher_name,
        board=board,
        grade=grade,
        subject=subject,
        start_date=start_date,
        end_date=end_date,
        instructions=instructions or 'None',
        weeks_json=weeks_json,
    )

    model = getattr(settings, "OPENROUTER_MODEL", "google/gemini-2.5-flash")
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    site_url = getattr(settings, "OPENROUTER_SITE_URL", "")
    app_name = getattr(settings, "OPENROUTER_APP_NAME", "")
    if site_url:
        headers["HTTP-Referer"] = site_url
    if app_name:
        headers["X-Title"] = app_name

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"OpenRouter error {response.status_code}: {response.text}")

    data = response.json()
    raw_text = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    try:
        return _extract_json_array(raw_text)
    except Exception as exc:
        # Persist raw output for debugging.
        debug_path = os.path.join(tempfile.gettempdir(), "openrouter_week_chunk_last.json")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(raw_text)
        raise RuntimeError(f"{exc} (raw output saved to {debug_path})")
