import re
import json
import logging
from collections import defaultdict
from backend.app.constants import FIELD_BOUNDS, _GEMINI_PROMPT
from backend.utils.logger import get_logger

logger = get_logger("pdf_parser")

_BGR_PATTERN = re.compile(
    r"(?i)"
    r"(?:post[\s\-]?prandial[\s\-]?(?:blood[\s\-]?)?(?:sugar|glucose)"
    r"|ppbs|rbs|random[\s\-]?blood[\s\-]?(?:sugar|glucose)"
    r"|post[\s\-]?meal[\s\-]?glucose"
    r"|2[\s\-]?hr[\s\-]?post"
    r"|pp[\s\-]?glucose"
    r")"
    r"[^\n\d]{0,50}?"
    r"((?:\d{1,4})(?:\.\d{1,2})?)"
)

_FBS_PATTERN = re.compile(
    r"(?i)"
    r"(?:fasting[\s\-]?(?:blood[\s\-]?)?(?:sugar|glucose|plasma[\s\-]?glucose)"
    r"|fbs|fpg|fbg|fasting[\s\-]?sugar"
    r")"
    r"[^\n\d]{0,50}?"
    r"((?:\d{1,4})(?:\.\d{1,2})?)"
)

_REGEX_PATTERNS = None

def _build_regex_patterns():
    try:
        from backend.utils.input_mapper import FEATURE_MAP
    except ImportError:
        FEATURE_MAP = {}

    reverse = defaultdict(list)
    for synonym, canonical in FEATURE_MAP.items():
        reverse[canonical].append(synonym)

    patterns = {}
    skip_auto = {"bgr", "glucose"}

    target_fields = set(FIELD_BOUNDS.keys()) - {"systolic_bp", "diastolic_bp"} - skip_auto
    for canonical in target_fields:
        synonyms = reverse.get(canonical, [])
        if canonical not in synonyms:
            synonyms.append(canonical)
        synonyms = sorted(synonyms, key=len, reverse=True)
        alts    = "|".join(re.escape(s) for s in synonyms)
        pattern = re.compile(
            r"(?i)\b(?:" + alts + r")\b"
            r"[^\n\d]{0,40}?"
            r"((?:\d{1,6})(?:\.\d{1,4})?)"
        )
        patterns[canonical] = pattern

    return patterns

def _get_regex_patterns():
    global _REGEX_PATTERNS
    if _REGEX_PATTERNS is None:
        _REGEX_PATTERNS = _build_regex_patterns()
    return _REGEX_PATTERNS

def extract_with_gemini(raw_text: str, api_key: str) -> dict | None:
    try:
        from google import genai as google_genai

        client  = google_genai.Client(api_key=api_key)
        prompt  = _GEMINI_PROMPT + raw_text

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        raw = response.text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            clean = re.sub(r"[^\x20-\x7E\n]", "", raw).strip()
            parsed = json.loads(clean)

        if not isinstance(parsed, dict):
            logger.warning("Gemini returned non-dict JSON; falling back to regex.")
            return None

        return {k: v for k, v in parsed.items() if v is not None}

    except Exception:
        logger.exception("Gemini extraction failed; falling back to regex.")
        return None

def extract_with_regex(text: str) -> dict:
    extracted = {}
    if not text:
        return extracted

    patterns = _get_regex_patterns()

    for canonical, pattern in patterns.items():
        if canonical not in FIELD_BOUNDS:
            continue
        match = pattern.search(text)
        if match:
            try:
                val = float(match.group(1))
                lo, hi = FIELD_BOUNDS[canonical]
                if lo <= val <= hi:
                    extracted[canonical] = val
            except (ValueError, KeyError):
                pass

    fbs_match = _FBS_PATTERN.search(text)
    if fbs_match:
        try:
            val = float(fbs_match.group(1))
            if FIELD_BOUNDS["glucose"][0] <= val <= FIELD_BOUNDS["glucose"][1]:
                extracted["glucose"] = val
        except ValueError:
            pass

    bgr_match = _BGR_PATTERN.search(text)
    if bgr_match:
        try:
            val = float(bgr_match.group(1))
            if FIELD_BOUNDS["bgr"][0] <= val <= FIELD_BOUNDS["bgr"][1]:
                extracted["bgr"] = val
        except ValueError:
            pass

    bp_match = re.search(r"\b(\d{2,3})\s*/\s*(\d{2,3})\b", text)
    if bp_match:
        sys_v, dia_v = float(bp_match.group(1)), float(bp_match.group(2))
        if 60 <= sys_v <= 260 and 30 <= dia_v <= 160:
            extracted["systolic_bp"]  = sys_v
            extracted["diastolic_bp"] = dia_v

    return extracted

def sanity_check(extracted: dict) -> dict:
    if not isinstance(extracted, dict):
        return {}
    cleaned = {}
    for field, value in extracted.items():
        if field not in FIELD_BOUNDS:
            continue
        try:
            val = float(value)
        except (TypeError, ValueError):
            continue
        lo, hi = FIELD_BOUNDS[field]
        if lo <= val <= hi:
            cleaned[field] = val
    return cleaned
