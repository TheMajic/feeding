from __future__ import annotations
import argparse
import sys
from .core import generate_from_text


def main(argv: list[str] | None = None) -> int:
    # Best-effort UTF-8 output on Windows consoles
    try:  # pragma: no cover
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    p = argparse.ArgumentParser(description="Generate a bilingual nutrition + workout plan from free text.")
    p.add_argument("text", help="User message containing height, weight, and sport.")
    p.add_argument(
        "--llm",
        dest="llm_base_model",
        default=None,
        help="Optional HuggingFace model name/path for stronger generation (requires transformers/torch).",
    )
    args = p.parse_args(argv)

    try:
        res = generate_from_text(args.text, llm_base_model=args.llm_base_model)
    except Exception as e:
        msg = str(e)
        # best-effort Arabic detection for error printing
        if any("\u0600" <= ch <= "\u06FF" for ch in (args.text or "")):
            print(f"خطأ: {msg}", file=sys.stderr)
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 2

    print(res.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

