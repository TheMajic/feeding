import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from feeding_ai.core import generate_from_text


def main() -> None:
    try:  # pragma: no cover
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    text = "طولي 175 سم ووزني 78 كجم وبمارس كرة قدم"
    res = generate_from_text(text)
    print(res.text)


if __name__ == "__main__":
    main()

