from __future__ import annotations
from dataclasses import dataclass
from typing import List
from ..lang import Lang
from ..nutrition import estimate_daily_targets, meal_templates, nutrient_examples, sport_type
from ..parser import Profile
from ..workouts import build_workout_plans


def _bmi(height_cm: float, weight_kg: float) -> float:
    m = max(0.5, height_cm / 100.0)
    return weight_kg / (m * m)


def _sport_type_label(lang: str, st: str) -> str:
    if lang == "ar":
        return {
            "endurance": "تحمّل (Endurance)",
            "strength": "قوة (Strength)",
            "mixed": "مختلط (Mixed)",
            "low": "خفيف (Low)",
        }.get(st, st)
    return st


def _sport_label(lang: str, sport_key: str, sport_raw: str) -> str:
    if lang == "ar":
        mapping = {
            "football": "كرة قدم",
            "basketball": "كرة سلة",
            "swimming": "سباحة",
            "running": "جري",
            "cycling": "دراجة",
            "tennis": "تنس",
            "volleyball": "كرة طائرة",
            "martial_arts": "فنون قتالية",
            "gym_strength": "جيم/حديد",
            "crossfit": "كروسفت",
            "yoga": "يوغا",
            "fitness": "لياقة عامة",
        }
        return mapping.get(sport_key, sport_raw)

    mapping = {
        "football": "football (soccer)",
        "basketball": "basketball",
        "swimming": "swimming",
        "running": "running",
        "cycling": "cycling",
        "tennis": "tennis",
        "volleyball": "volleyball",
        "martial_arts": "martial arts",
        "gym_strength": "gym/strength training",
        "crossfit": "crossfit",
        "yoga": "yoga",
        "fitness": "general fitness",
    }
    return mapping.get(sport_key, sport_raw)


@dataclass(frozen=True)
class RuleBasedGenerator:
    """
    Deterministic baseline generator.
    - Strong enough to be useful immediately.
    - Also used to synthesize training data for SFT/LoRA.
    """

    def generate(self, profile: Profile, lang: Lang) -> str:
        lang_code = lang.code
        targets = estimate_daily_targets(profile)
        bmi = _bmi(profile.height_cm, profile.weight_kg)
        st = sport_type(profile.sport)
        st_label = _sport_type_label(lang_code, st)

        sport_name = _sport_label(lang_code, profile.sport, profile.sport_raw)
        meals = meal_templates(lang_code)
        ex = nutrient_examples(lang_code)
        workout_plans = build_workout_plans(lang_code, profile.sport)

        if lang_code == "ar":
            lines: List[str] = []
            lines.append("## خطة غذائية + تمارين (مولّدة تلقائيًا)")
            lines.append("")
            lines.append("### بياناتك")
            lines.append(f"- **الطول**: {profile.height_cm:.0f} سم")
            lines.append(f"- **الوزن**: {profile.weight_kg:.1f} كجم")
            lines.append(f"- **الرياضة**: {sport_name}")
            lines.append(f"- **BMI تقريبي**: {bmi:.1f}")
            lines.append("")
            lines.append("### أهداف يومية (تقديرية)")
            lines.append(f"- **السعرات**: {targets.calories_kcal} kcal/يوم")
            lines.append(f"- **بروتين**: {targets.protein_g} g")
            lines.append(f"- **كربوهيدرات**: {targets.carbs_g} g")
            lines.append(f"- **دهون**: {targets.fats_g} g")
            lines.append(f"- **مياه**: {targets.water_liters:.1f} لتر (زود مع التعرّق)")
            lines.append("")
            lines.append("### 3 وجبات (مكوّنات + عناصر غذائية + أمثلة)")
            for meal in meals:
                lines.append(f"#### {meal.name}")
                for c in meal.components:
                    lines.append(f"- {c}")
                lines.append(f"- **تركيز عناصر**: {', '.join(meal.nutrients_focus)}")
                lines.append("")
            lines.append("### أمثلة منتجات/أطعمة حسب العنصر")
            for k, items in ex.items():
                lines.append(f"- **{k}**: " + "، ".join(items))
            lines.append("")
            lines.append("### تمارين مقترحة (جيم + منزل)")
            lines.append(f"- **نمط رياضي مستنتج**: {st_label}")
            for wp in workout_plans:
                lines.append(f"#### {wp.title}")
                for d in wp.days:
                    lines.append(f"- {d}")
                if wp.notes:
                    lines.append("- **ملاحظات**:")
                    for n in wp.notes:
                        lines.append(f"  - {n}")
                lines.append("")
            lines.append("### ملاحظات سريعة للتعافي")
            lines.append("- نوم 7-9 ساعات.")
            lines.append("- بعد التمرين: وجبة فيها بروتين + كربوهيدرات خلال 1-3 ساعات.")
            lines.append("- لو هدفك تخسيس/زيادة وزن: قلّل/زوّد 200-300 kcal وراقب التغيير أسبوعيًا.")
            return "\n".join(lines)

        # English
        lines = []
        lines.append("## Auto-generated Nutrition + Training Plan")
        lines.append("")
        lines.append("### Your profile")
        lines.append(f"- **Height**: {profile.height_cm:.0f} cm")
        lines.append(f"- **Weight**: {profile.weight_kg:.1f} kg")
        lines.append(f"- **Sport**: {sport_name}")
        lines.append(f"- **Estimated BMI**: {bmi:.1f}")
        lines.append("")
        lines.append("### Daily targets (estimated)")
        lines.append(f"- **Calories**: {targets.calories_kcal} kcal/day")
        lines.append(f"- **Protein**: {targets.protein_g} g")
        lines.append(f"- **Carbs**: {targets.carbs_g} g")
        lines.append(f"- **Fats**: {targets.fats_g} g")
        lines.append(f"- **Water**: {targets.water_liters:.1f} L (increase with sweating)")
        lines.append("")
        lines.append("### 3 meals (ingredients + nutrients + examples)")
        for meal in meals:
            lines.append(f"#### {meal.name}")
            for c in meal.components:
                lines.append(f"- {c}")
            lines.append(f"- **Nutrient focus**: {', '.join(meal.nutrients_focus)}")
            lines.append("")
        lines.append("### Food examples by nutrient")
        for k, items in ex.items():
            lines.append(f"- **{k}**: " + ", ".join(items))
        lines.append("")
        lines.append("### Suggested workouts (Gym + Home)")
        lines.append(f"- **Inferred sport type**: {st_label}")
        for wp in workout_plans:
            lines.append(f"#### {wp.title}")
            for d in wp.days:
                lines.append(f"- {d}")
            if wp.notes:
                lines.append("- **Notes**:")
                for n in wp.notes:
                    lines.append(f"  - {n}")
            lines.append("")
        lines.append("### Quick recovery notes")
        lines.append("- Sleep 7-9 hours.")
        lines.append("- Post-workout: protein + carbs within 1-3 hours.")
        lines.append("- For fat loss/gain: adjust +/-200-300 kcal and track weekly.")
        return "\n".join(lines)

