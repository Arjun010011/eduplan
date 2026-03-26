import json
import logging
import os
import re
import tempfile

import requests
from django.conf import settings

LESSON_CHUNK_PROMPT_TEMPLATE = """
You are an expert curriculum designer for Indian school boards.

Generate highly detailed and comprehensive lesson plan content in JSON for the following:
- Board: {board}
- Grade: {grade}
- Subject: {subject}
- Teacher Name: {teacher_name}
- Special Instructions: {instructions}

CRITICAL: You MUST strictly follow the official {board} syllabus for Grade {grade} {subject}. Ensure all chapter and topic names are 100% accurate.

Input lessons (JSON array). Each item includes lesson_no:
{lessons_json}

Output Format: You MUST return a VALID JSON array of objects. 
Each object MUST have these exact keys: "lesson_no", "topic", "objectives", "activities".

Example structure for 2 lessons:
[
  {{"lesson_no": 1, "topic": "Accurate Chapter Name", "objectives": ["Obj 1", "Obj 2", "Obj 3"], "activities": ["Act 1", "Act 2", "Act 3"]}},
  {{"lesson_no": 2, "topic": "Next Chapter", "objectives": ["Obj 1", "Obj 2", "Obj 3"], "activities": ["Act 1", "Act 2", "Act 3"]}}
]

CRITICAL RULES:
1. STRICT JSON ONLY. No markdown fences, no commentary.
2. DO NOT use double quotes (") inside your string values. Use single quotes (') if needed.
3. You must create a SEPARATE object for EACH lesson_no provided in the input. Do NOT merge them.
4. "objectives" and "activities" must be arrays of 3 to 5 highly detailed items.
""".strip()


def _extract_json_array(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    if "[" in text and "]" in text:
        # Prefer a JSON array that starts with "[{" and ends with "}]" if present.
        start = None
        end = None
        start_match = re.search(r"\[\s*\{", text)
        if start_match:
            start = start_match.start()
            end_matches = list(re.finditer(r"\}\s*\]", text))
            if end_matches:
                end = end_matches[-1].end()
        if start is None or end is None:
            start = text.find("[")
            end = text.rfind("]")
            end = end + 1 if end != -1 else len(text)
        text = text[start:end]
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    # If the model was cut off inside a string value (odd number of unescaped
    # quotes), close the string before balancing brackets/braces.
    unescaped_quotes = len(re.findall(r'(?<!\\)"', text))
    if unescaped_quotes % 2 != 0:
        text = text.rstrip() + '"'

    # Balance brackets/braces if the model truncates near the end.
    open_brackets = text.count("[")
    close_brackets = text.count("]")
    if open_brackets > close_brackets:
        text = text + ("]" * (open_brackets - close_brackets))
    open_braces = text.count("{")
    close_braces = text.count("}")
    if open_braces > close_braces:
        text = text + ("}" * (open_braces - close_braces))

    decoder = json.JSONDecoder()
    try:
        # raw_decode stops at the end of the first valid JSON value, ignoring
        # any trailing text the model may append after the array.
        result, _ = decoder.raw_decode(text)
        return result
    except json.JSONDecodeError:
        # Heuristic repairs for missing commas and braces.
        repaired = text
        repaired = re.sub(r"}\s*{", "},{", repaired)
        repaired = re.sub(r"\]\s*,\s*{", "]},{", repaired)
        repaired = re.sub(r"\]\"\s*}", "]}", repaired)  # Fix rogue `]"` instead of `]`
        repaired = re.sub(r"\]\s*\]\s*}", "]}", repaired)  # Fix rogue `]]}` instead of `]}`
        repaired = re.sub(r"\"\s*(?=[A-Za-z_][A-Za-z0-9_]*\"\s*:)", "\",", repaired)
        repaired = re.sub(r"\]\s*(?=[A-Za-z_][A-Za-z0-9_]*\"\s*:)", "],", repaired)
        repaired = re.sub(r"}\s*(?=[A-Za-z_][A-Za-z0-9_]*\"\s*:)", "},", repaired)
        
        try:
            result, _ = decoder.raw_decode(repaired)
            return result
        except json.JSONDecodeError as e:
            # Last-resort salvage: split on lesson_no objects and rebuild a clean array.
            chunks = re.split(r"(?=\{\s*\"lesson_no\"\s*:)", text)
            objects = []
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue
                if not chunk.startswith("{"):
                    continue
                # Trim anything after the last closing brace if present.
                last_brace = chunk.rfind("}")
                if last_brace != -1:
                    chunk = chunk[: last_brace + 1]
                # Balance braces if truncated.
                open_braces = chunk.count("{")
                close_braces = chunk.count("}")
                if open_braces > close_braces:
                    chunk = chunk + ("}" * (open_braces - close_braces))
                try:
                    obj, _ = decoder.raw_decode(chunk)
                    if isinstance(obj, dict):
                        objects.append(obj)
                except json.JSONDecodeError:
                    continue
            if objects:
                return objects
            raise ValueError(f"JSON repair failed: {e}. Raw text: {text}")


def generate_lesson_details(teacher_name, board, grade, subject, instructions, lesson_chunk):
    """
    Calls OpenRouter with a structured lesson prompt.
    Returns a list of lesson dicts with topic/objectives/activities.
    """
    lessons_json = json.dumps(lesson_chunk, ensure_ascii=False, separators=(",", ":"))

    prompt = LESSON_CHUNK_PROMPT_TEMPLATE.format(
        teacher_name=teacher_name,
        board=board,
        grade=grade,
        subject=subject,
        instructions=instructions or 'None',
        lessons_json=lessons_json,
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
    raw_text = ""
    choices = data.get("choices", [])
    if choices:
        message = choices[0].get("message", {}) or {}
        raw_text = message.get("content")
        if not raw_text:
            # Some OpenRouter models emit content in a separate reasoning field.
            raw_text = message.get("reasoning")
        if not raw_text:
            # Some models return a list of reasoning parts.
            reasoning_parts = message.get("reasoning_details")
            if isinstance(reasoning_parts, list):
                collected = []
                for part in reasoning_parts:
                    if isinstance(part, dict):
                        text = part.get("text")
                        if text:
                            collected.append(text)
                if collected:
                    raw_text = "\n".join(collected)
        if not raw_text:
            # Fallback for older-style completions.
            raw_text = choices[0].get("text")

    if raw_text is None:
        raw_text = ""

    logger = logging.getLogger(__name__)
    try:
        if not raw_text:
            # Avoid hard-failing when providers return empty content.
            logger.warning("OpenRouter returned empty content; using fallback empty lesson list.")
            debug_path = os.path.join(tempfile.gettempdir(), "openrouter_lesson_chunk_last.json")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(str(data))
            return []
        parsed = _extract_json_array(raw_text)
        if not isinstance(parsed, list):
            logger.warning("OpenRouter returned non-array JSON; using fallback empty lesson list.")
            return []
        return parsed
    except Exception as exc:
        # Persist raw output for debugging and allow request to complete.
        debug_path = os.path.join(tempfile.gettempdir(), "openrouter_lesson_chunk_last.json")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(str(raw_text))
        logger.warning("OpenRouter JSON parsing failed: %s", exc)
        return []
