from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple
from .parser import Profile

SportType = Literal["endurance", "strength", "mixed", "low"]

def sport_type(sport_key: str) -> SportType:
    s = (sport_key or "").lower()
    if s in {"running", "swimming", "cycling"}:
        return "endurance"
    if s in {"football", "basketball", "tennis", "volleyball"}:
        return "mixed"
    if s in {"gym_strength", "crossfit", "martial_arts"}:
        return "strength"
    if s in {"yoga"}:
        return "low"
    if s in {"fitness"}:
        return "mixed"
    return "mixed"


@dataclass(frozen=True)
class DailyTargets:
    calories_kcal: int
    protein_g: int
    carbs_g: int
    fats_g: int
    water_liters: float


@dataclass(frozen=True)
class Meal:
    name: str
    macro_split: Tuple[float, float, float]  # (protein, carbs, fats) ratio for the meal
    components: List[str]  # human readable
    nutrients_focus: List[str]


def estimate_daily_targets(profile: Profile) -> DailyTargets:
    wt = float(profile.weight_kg)
    st = sport_type(profile.sport)

    # Simple energy estimate by sport intensity (kcal/kg)
    kcal_per_kg = {"low": 30.0, "mixed": 33.0, "endurance": 35.0, "strength": 34.0}[st]
    calories = int(round(wt * kcal_per_kg))
    calories = max(1600, min(4200, calories))

    protein_per_kg = {"low": 1.6, "mixed": 1.8, "endurance": 1.6, "strength": 2.0}[st]
    protein_g = int(round(wt * protein_per_kg))

    fat_per_kg = 0.9 if st in {"strength", "mixed"} else 0.8
    fats_g = int(round(wt * fat_per_kg))
    fats_g = max(45, min(120, fats_g))

    # Remaining calories -> carbs
    protein_kcal = protein_g * 4
    fat_kcal = fats_g * 9
    remaining = max(0, calories - protein_kcal - fat_kcal)
    carbs_g = int(round(remaining / 4))

    water_liters = round(max(2.0, min(5.0, wt * 0.035)), 1)

    return DailyTargets(
        calories_kcal=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fats_g=fats_g,
        water_liters=water_liters,
    )


def meal_templates(lang: str) -> List[Meal]:
    if lang == "ar":
        return [
            Meal(
                name="الفطار",
                macro_split=(0.30, 0.35, 0.35),
                components=[
                    "مصدر بروتين: 2-3 بيض أو زبادي/لبن يوناني أو فول/حمص",
                    "كربوهيدرات مع ألياف: شوفان أو خبز حبوب كاملة أو بطاطس",
                    "دهون صحية: مكسرات أو زبدة فول سوداني أو أفوكادو",
                    "فاكهة + خضار (حسب المتاح)",
                ],
                nutrients_focus=["بروتين", "ألياف", "كالسيوم", "بوتاسيوم"],
            ),
            Meal(
                name="الغداء",
                macro_split=(0.35, 0.45, 0.20),
                components=[
                    "بروتين عالي الجودة: دجاج/سمك/لحم خالي دهون/عدس",
                    "كربوهيدرات معقدة: رز/مكرونة قمح كامل/برغل/بطاطا",
                    "خضار متنوعة: سلطة كبيرة أو خضار مطبوخ",
                    "دهون: زيت زيتون أو طحينة (كمية صغيرة)",
                ],
                nutrients_focus=["حديد", "زنك", "مغنيسيوم", "فيتامينات A/C"],
            ),
            Meal(
                name="العشاء",
                macro_split=(0.35, 0.30, 0.35),
                components=[
                    "بروتين: تونة/جبنة قريش/بيض/بقوليات",
                    "خضار: شوربة خضار أو سلطة أو خضار سوتيه",
                    "كربوهيدرات خفيفة حسب التمرين: خبز حبوب كاملة أو فاكهة",
                    "دهون صحية: زيت زيتون/مكسرات (كمية صغيرة)",
                ],
                nutrients_focus=["تعافي عضلي", "أوميجا-3 (لو سمك)", "ألياف"],
            ),
        ]

    # English
    return [
        Meal(
            name="Breakfast",
            macro_split=(0.30, 0.35, 0.35),
            components=[
                "Protein: 2-3 eggs or Greek yogurt/milk or beans (fava/chickpeas)",
                "Fiber carbs: oats or whole-grain bread or potatoes",
                "Healthy fats: nuts or peanut butter or avocado",
                "Fruit + veggies (as available)",
            ],
            nutrients_focus=["protein", "fiber", "calcium", "potassium"],
        ),
        Meal(
            name="Lunch",
            macro_split=(0.35, 0.45, 0.20),
            components=[
                "High-quality protein: chicken/fish/lean meat/lentils",
                "Complex carbs: rice/whole-wheat pasta/bulgur/sweet potatoes",
                "Mixed vegetables: big salad or cooked veggies",
                "Fats: olive oil or tahini (small amount)",
            ],
            nutrients_focus=["iron", "zinc", "magnesium", "vitamins A/C"],
        ),
        Meal(
            name="Dinner",
            macro_split=(0.35, 0.30, 0.35),
            components=[
                "Protein: tuna/cottage cheese/eggs/legumes",
                "Vegetables: veggie soup or salad or sauteed veggies",
                "Light carbs depending on training: whole-grain bread or fruit",
                "Healthy fats: olive oil/nuts (small amount)",
            ],
            nutrients_focus=["recovery", "omega-3 (if fish)", "fiber"],
        ),
    ]


def nutrient_examples(lang: str) -> Dict[str, List[str]]:
    if lang == "ar":
        return {
            "بروتين": ["صدور دجاج", "تونة/سردين", "بيض", "لبن/زبادي يوناني", "عدس/فول/حمص"],
            "كربوهيدرات": ["شوفان", "رز", "مكرونة قمح كامل", "بطاطس/بطاطا", "خبز حبوب كاملة"],
            "دهون صحية": ["زيت زيتون", "مكسرات", "طحينة", "أفوكادو", "بذور الكتان/الشيا"],
            "ألياف": ["خضار ورقية", "خيار/طماطم", "تفاح/كمثرى", "شوفان", "بقوليات"],
            "إلكتروليت": ["موز (بوتاسيوم)", "زبادي (صوديوم/بوتاسيوم)", "مياه + رشة ملح بعد التعرّق الشديد"],
        }
    return {
        "Protein": ["chicken breast", "tuna/sardines", "eggs", "Greek yogurt/milk", "lentils/beans/chickpeas"],
        "Carbs": ["oats", "rice", "whole-wheat pasta", "potatoes/sweet potatoes", "whole-grain bread"],
        "Healthy fats": ["olive oil", "nuts", "tahini", "avocado", "flax/chia seeds"],
        "Fiber": ["leafy greens", "cucumber/tomato", "apples/pears", "oats", "legumes"],
        "Electrolytes": ["banana (potassium)", "yogurt (sodium/potassium)", "water + a pinch of salt after heavy sweating"],
    }

