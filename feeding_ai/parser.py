from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

from .lang import Lang


@dataclass(frozen=True)
class Profile:
    height_cm: float
    weight_kg: float
    sport: str  # canonical key
    sport_raw: str


_ARABIC_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_EXT_ARABIC_INDIC_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def _normalize_numbers(text: str) -> str:
    return (text or "").translate(_ARABIC_INDIC_DIGITS).translate(_EXT_ARABIC_INDIC_DIGITS)


def _first_float(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _parse_height_cm(text: str) -> Optional[float]:
    t = _normalize_numbers(text).lower()

    # meters
    m = re.search(r"(\d+(?:\.\d+)?)\s*(m|meter|meters|metre|metres|م)\b", t)
    if m:
        val = float(m.group(1))
        # if someone writes 175 m by mistake, ignore meters rule
        if 1.0 <= val <= 2.5:
            return val * 100.0

    # centimeters
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*(cm|centimeter|centimeters|centimetre|centimetres|سم)\b",
        t,
    )
    if m:
        val = float(m.group(1))
        if 90 <= val <= 250:
            return val

    # Arabic phrasing: "طولي 175" (assume cm if plausible)
    m = re.search(r"(?:height|tall|طولي|الطول)\s*[:\-]?\s*(\d+(?:\.\d+)?)", t)
    if m:
        val = float(m.group(1))
        if 90 <= val <= 250:
            return val
        if 1.0 <= val <= 2.5:
            return val * 100.0

    # Last resort: any standalone number that looks like cm
    val = _first_float(t)
    if val is not None and 90 <= val <= 250:
        return val

    return None


def _parse_weight_kg(text: str) -> Optional[float]:
    t = _normalize_numbers(text).lower()

    # pounds
    m = re.search(r"(\d+(?:\.\d+)?)\s*(lb|lbs|pound|pounds)\b", t)
    if m:
        val = float(m.group(1))
        if 50 <= val <= 600:
            return val * 0.45359237

    # kilograms
    m = re.search(r"(\d+(?:\.\d+)?)\s*(kg|كيلو|كجم|كيلوجرام|كيلوغرام)\b", t)
    if m:
        val = float(m.group(1))
        if 25 <= val <= 300:
            return val

    # Arabic phrasing: "وزني 78"
    m = re.search(r"(?:weight|وزني|الوزن)\s*[:\-]?\s*(\d+(?:\.\d+)?)", t)
    if m:
        val = float(m.group(1))
        if 25 <= val <= 300:
            return val

    return None


# Canonical sport keys + synonyms (AR/EN)
_SPORT_SYNONYMS = {
    "football": ["football","soccer","كرة قدم","كورة قدم","كرةالقدم","soccer player",],
    "basketball": ["basketball", "كرة سلة", "كورة سلة", "basket ball"],
    "swimming": ["swimming", "swim", "سباحة", "السباحة"],
    "running": ["running", "run", "jogging", "جري", "جرى", "العدو", "ركض"],
    "cycling": ["cycling", "bike", "biking", "دراجة", "دراجات", "عجلة"],
    "tennis": ["tennis", "تنس", "كرة المضرب"],
    "volleyball": ["volleyball", "كرة طائرة", "كورة طائرة"],
    "martial_arts": ["martial", "mma", "boxing", "kickboxing", "karate", "taekwondo", "ملاكمة", "كاراتيه", "تايكوندو", "فنون قتالية"],
    "gym_strength": ["gym", "weightlifting", "weights", "strength", "bodybuilding", "جيم", "حديد", "كمال اجسام", "كمال أجسام", "قوة", "رفع اثقال", "رفع أثقال"],
    "crossfit": ["crossfit", "كروسفت", "كروس فيت"],
    "yoga": ["yoga", "يوغا"],
    "fitness": ["fitness", "لياقة", "لياقه", "تمارين منزلية", "home workout", "calisthenics"],
}


def _detect_sport(text: str) -> Tuple[Optional[str], Optional[str]]:
    t = (text or "").lower()
    # Check longer synonyms first to reduce false positives
    pairs = []
    for k, syns in _SPORT_SYNONYMS.items():
        for s in syns:
            pairs.append((k, s))
    pairs.sort(key=lambda x: len(x[1]), reverse=True)

    for key, syn in pairs:
        if syn.lower() in t:
            return key, syn

    # fallback: try to pick last word-ish after "sport"/"رياضة"
    m = re.search(r"(?:sport|رياضة|الرياضة|بلعب|بمارس|أمارس)\s*[:\-]?\s*([^\n\r,\.]+)", text or "", flags=re.IGNORECASE)
    if m:
        raw = m.group(1).strip()
        if raw:
            return raw.strip().lower().replace(" ", "_"), raw

    return None, None


def parse_profile(text: str, lang: Lang) -> Profile:
    height_cm = _parse_height_cm(text)
    weight_kg = _parse_weight_kg(text)
    sport_key, sport_raw = _detect_sport(text)

    missing = []
    if height_cm is None:
        missing.append("height" if lang.code == "en" else "الطول")
    if weight_kg is None:
        missing.append("weight" if lang.code == "en" else "الوزن")
    if sport_key is None:
        missing.append("sport" if lang.code == "en" else "الرياضة")

    if missing:
        if lang.code == "ar":
            raise ValueError(f"محتاج معلومات ناقصة: {', '.join(missing)}. مثال: طولي 175 سم ووزني 78 كجم وبمارس كرة قدم")
        raise ValueError(f"Missing fields: {', '.join(missing)}. Example: I am 180 cm, 82 kg, I play basketball")

    assert height_cm is not None and weight_kg is not None and sport_key is not None and sport_raw is not None
    return Profile(height_cm=float(height_cm), weight_kg=float(weight_kg), sport=str(sport_key), sport_raw=str(sport_raw))