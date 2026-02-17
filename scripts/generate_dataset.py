from __future__ import annotations

import argparse
import json
import os
import random
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from feeding_ai.generators.rule_based import RuleBasedGenerator
from feeding_ai.lang import Lang
from feeding_ai.parser import parse_profile


SPORTS = [
    ("football", "كرة قدم", "football"),
    ("basketball", "كرة سلة", "basketball"),
    ("swimming", "السباحة", "swimming"),
    ("running", "الجري", "running"),
    ("cycling", "ركوب الدراجات", "cycling"),
    ("gym_strength", "الجيم/الحديد", "gym"),
    ("martial_arts", "ملاكمة", "boxing"),
    ("crossfit", "كروسفت", "crossfit"),
    ("yoga", "يوغا", "yoga"),
]


def make_prompt(lang: str, height_cm: int, weight_kg: int, sport_ar: str, sport_en: str) -> str:
    if lang == "ar":
        templates = [
            f"طولي {height_cm} سم ووزني {weight_kg} كجم وبمارس {sport_ar}",
            f"الطول: {height_cm} سم، الوزن: {weight_kg} كجم، الرياضة: {sport_ar}",
            f"أنا طولي {height_cm} سم ووزني {weight_kg} كيلو وبلعب {sport_ar}. عايز نظام غذائي وتمارين.",
        ]
        return random.choice(templates)
    templates = [
        f"I am {height_cm} cm, {weight_kg} kg, I do {sport_en}",
        f"Height: {height_cm} cm, Weight: {weight_kg} kg, Sport: {sport_en}",
        f"My height is {height_cm} cm and my weight is {weight_kg} kg. I play {sport_en}. Need a meal plan and workouts.",
    ]
    return random.choice(templates)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output JSONL path.")
    ap.add_argument("--n", type=int, default=2000, help="Number of samples.")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    gen = RuleBasedGenerator()

    with out_path.open("w", encoding="utf-8") as f:
        for i in range(int(args.n)):
            lang = "ar" if (i % 2 == 0) else "en"
            _, sport_ar, sport_en = random.choice(SPORTS)
            height_cm = random.randint(150, 200)
            weight_kg = random.randint(45, 120)

            prompt = make_prompt(lang, height_cm, weight_kg, sport_ar, sport_en)
            profile = parse_profile(prompt, Lang(lang))
            completion = gen.generate(profile, Lang(lang))

            rec = {
                "id": str(uuid.uuid4()),
                "lang": lang,
                "prompt": prompt,
                "profile": {
                    "height_cm": profile.height_cm,
                    "weight_kg": profile.weight_kg,
                    "sport": profile.sport,
                    "sport_raw": profile.sport_raw,
                },
                "completion": completion,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {args.n} samples to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

