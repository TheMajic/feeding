from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .nutrition import sport_type


@dataclass(frozen=True)
class WorkoutPlan:
    title: str
    days: List[str]  # each item is a formatted day plan
    notes: List[str]


def build_workout_plans(lang: str, sport_key: str) -> List[WorkoutPlan]:
    st = sport_type(sport_key)
    if lang == "ar":
        return _arabic_plans(st)
    return _english_plans(st)


def _arabic_plans(st: str) -> List[WorkoutPlan]:
    common_notes = [
        "إحماء 8-12 دقيقة (مشي سريع/نط حبل خفيف + حركات مفصلية).",
        "حافظ على التقنية الصحيحة، وزوّد الأحمال تدريجيًا.",
        "لو عندك إصابة أو ألم حاد: أوقف التمرين واستشر مختص.",
    ]

    if st == "endurance":
        gym = WorkoutPlan(
            title="خطة جيم (4 أيام) - تركيز تحمل + قوة داعمة",
            days=[
                "اليوم 1 (قوة الجزء السفلي): سكوات 3x5-8، Romanian Deadlift 3x6-10، لانجز 3x10/رجل، كالف 3x12-15، كور 3x30-45ث",
                "اليوم 2 (قوة الجزء العلوي): بنش 3x6-10، سحب أرضي/Lat Pulldown 3x8-12، ضغط كتف 3x6-10، Face Pull 3x12-15، بايسبس/ترايسبس 2x10-12",
                "اليوم 3 (تحمل عضلي): Leg Press 3x12-15، Hip Thrust 3x10-12، Push-ups 3xAMRAP، Row 3x12، Farmer Walk 4x30م",
                "اليوم 4 (كونديشنينج): 6-10 عدّات جري 30-60ث شدة عالية + راحة 60-90ث، ثم إطالات 10د",
            ],
            notes=common_notes + ["أضف جلسة سهلة (Zone 2) 30-45 دقيقة 1-2 مرة/أسبوع حسب رياضتك الأساسية."],
        )
    elif st == "strength":
        gym = WorkoutPlan(
            title="خطة جيم (4 أيام) - قوة/كتلة",
            days=[
                "اليوم 1 (Upper): بنش 4x5-8، Row 4x6-10، ضغط كتف 3x6-10، سحب علوي 3x8-12، ذراع 2x10-12",
                "اليوم 2 (Lower): سكوات 4x5-8، ديدلفت/Trap Bar 3x3-6، لانجز 3x10، كالف 3x12-15، كور 3x45ث",
                "اليوم 3 (Upper): Incline بنش 3x6-10، Pull-ups/Lat 3x6-12، Dips 3x6-12، Rear Delt 3x12-15، ذراع 2x10-12",
                "اليوم 4 (Lower + Conditioning خفيف): Front Squat أو Leg Press 3x6-12، RDL 3x6-10، Hip Thrust 3x8-12، مشي مائل 15-25د",
            ],
            notes=common_notes + ["للكتلة: زوّد السعرات قليلًا، وللقوة: ركّز على التقدم بالأوزان."],
        )
    else:  # mixed/low
        gym = WorkoutPlan(
            title="خطة جيم (3 أيام) - لياقة عامة + دعم للرياضة",
            days=[
                "اليوم 1 (Full body): سكوات 3x6-10، بنش 3x6-10، Row 3x8-12، كور 3x30-45ث",
                "اليوم 2 (Full body): ديدلفت خفيف/RDL 3x6-10، ضغط كتف 3x6-10، Lat Pulldown 3x8-12، لانجز 2x10/رجل",
                "اليوم 3 (Full body + Conditioning): Leg Press 3x10-15، Push-ups 3xAMRAP، Row 3x10-15، نط حبل/جري خفيف 12-20د",
            ],
            notes=common_notes + ["زود/قلل الكارديو حسب شدة رياضتك الأساسية."],
        )

    home = WorkoutPlan(
        title="خطة منزلية/لياقة (3 أيام) - بدون أجهزة",
        days=[
            "اليوم 1: Squat 4x12-20، Push-ups 4xAMRAP، Plank 4x30-60ث، Glute Bridge 3x15-25",
            "اليوم 2: Lunges 4x10/رجل، Pike Push-ups 3x8-15، Superman 3x12-20، Side Plank 3x30ث/جانب",
            "اليوم 3: Burpees 6x8-12 (راحة 60-90ث)، Mountain Climbers 4x30-45ث، Hollow Hold 4x20-40ث، إطالات 10د",
        ],
        notes=common_notes + ["لو عندك دمبلز/أستيك: ممكن نزود مقاومة بسهولة."],
    )

    return [gym, home]


def _english_plans(st: str) -> List[WorkoutPlan]:
    common_notes = [
        "Warm up 8-12 min (easy cardio + joint mobility).",
        "Prioritize form and progress gradually.",
        "If you have an injury or sharp pain: stop and consult a professional.",
    ]

    if st == "endurance":
        gym = WorkoutPlan(
            title="Gym plan (4 days) - endurance + supportive strength",
            days=[
                "Day 1 (Lower strength): Squat 3x5-8, Romanian Deadlift 3x6-10, Lunges 3x10/leg, Calf raises 3x12-15, Core 3x30-45s",
                "Day 2 (Upper strength): Bench 3x6-10, Row/Lat Pulldown 3x8-12, Overhead Press 3x6-10, Face Pull 3x12-15, Arms 2x10-12",
                "Day 3 (Muscular endurance): Leg Press 3x12-15, Hip Thrust 3x10-12, Push-ups 3xAMRAP, Row 3x12, Farmer Walk 4x30m",
                "Day 4 (Conditioning): 6-10 intervals of 30-60s hard + 60-90s rest, then stretch 10 min",
            ],
            notes=common_notes + ["Add 1-2 easy Zone-2 sessions (30-45 min) depending on your sport schedule."],
        )
    elif st == "strength":
        gym = WorkoutPlan(
            title="Gym plan (4 days) - strength/hypertrophy",
            days=[
                "Day 1 (Upper): Bench 4x5-8, Row 4x6-10, OHP 3x6-10, Lat Pulldown 3x8-12, Arms 2x10-12",
                "Day 2 (Lower): Squat 4x5-8, Deadlift/Trap Bar 3x3-6, Lunges 3x10, Calves 3x12-15, Core 3x45s",
                "Day 3 (Upper): Incline Bench 3x6-10, Pull-ups/Lat 3x6-12, Dips 3x6-12, Rear delts 3x12-15, Arms 2x10-12",
                "Day 4 (Lower + light cardio): Front Squat or Leg Press 3x6-12, RDL 3x6-10, Hip Thrust 3x8-12, Incline walk 15-25 min",
            ],
            notes=common_notes + ["For muscle gain: slight calorie surplus. For strength: focus on adding weight/reps week to week."],
        )
    else:
        gym = WorkoutPlan(
            title="Gym plan (3 days) - general fitness + sport support",
            days=[
                "Day 1 (Full body): Squat 3x6-10, Bench 3x6-10, Row 3x8-12, Core 3x30-45s",
                "Day 2 (Full body): Light Deadlift/RDL 3x6-10, OHP 3x6-10, Lat Pulldown 3x8-12, Lunges 2x10/leg",
                "Day 3 (Full body + conditioning): Leg Press 3x10-15, Push-ups 3xAMRAP, Row 3x10-15, Jump rope/easy run 12-20 min",
            ],
            notes=common_notes + ["Increase/decrease cardio based on your sport intensity and recovery."],
        )

    home = WorkoutPlan(
        title="Home/Fitness plan (3 days) - no equipment",
        days=[
            "Day 1: Squat 4x12-20, Push-ups 4xAMRAP, Plank 4x30-60s, Glute Bridge 3x15-25",
            "Day 2: Lunges 4x10/leg, Pike Push-ups 3x8-15, Superman 3x12-20, Side Plank 3x30s/side",
            "Day 3: Burpees 6x8-12 (60-90s rest), Mountain Climbers 4x30-45s, Hollow Hold 4x20-40s, Stretch 10 min",
        ],
        notes=common_notes + ["If you have dumbbells/bands, we can easily increase resistance."],
    )

    return [gym, home]

