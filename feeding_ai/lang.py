from __future__ import annotations

import re
from dataclasses import dataclass

try:
    from langdetect import DetectorFactory, detect  # type: ignore

    DetectorFactory.seed = 42
except Exception:  # pragma: no cover
    detect = None  # type: ignore


_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")


@dataclass(frozen=True)
class Lang:
    code: str  # "ar" | "en"


def detect_lang(text: str) -> Lang:
    if _ARABIC_RE.search(text or ""):
        return Lang("ar")
    try:
        if detect is None:
            return Lang("en")
        code = detect(text)  # type: ignore[misc]
        return Lang("ar" if str(code).startswith("ar") else "en")
    except Exception:
        return Lang("en")

