from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return {"bmi": round(bmi, 1), "category": category}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: Optional[str]) -> Dict[str, Any]:
    gender_norm = (gender or "other").lower()
    if gender_norm == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif gender_norm == "female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 78
    return {"bmr": round(bmr, 0), "formula": "Mifflin-St Jeor"}


ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very active": 1.9,
}


def calculate_tdee(bmr: float, activity_level: str) -> Dict[str, Any]:
    key = _normalize(activity_level)
    factor = ACTIVITY_FACTORS.get(key, 1.45)
    tdee = bmr * factor
    return {"tdee": round(tdee, 0), "factor": factor, "activity_level": key}


def calorie_target(tdee: float, goal: str) -> Dict[str, Any]:
    g = _normalize(goal)
    if any(x in g for x in ["fat loss", "loss", "cut", "reduce", "lose weight"]):
        target = tdee - 400
        mode = "fat_loss"
    elif any(x in g for x in ["muscle", "bulk", "gain", "mass"]):
        target = tdee + 250
        mode = "muscle_gain"
    else:
        target = tdee
        mode = "maintenance"
    return {"mode": mode, "calories_per_day": round(max(target, 1200), 0)}


def macro_split(calories: float, protein_g_per_kg: float = 1.8, weight_kg: Optional[float] = None) -> Dict[str, Any]:
    protein_g = protein_g_per_kg * weight_kg if weight_kg else calories * 0.25 / 4
    fat_g = calories * 0.25 / 9
    carbs_g = max((calories - protein_g * 4 - fat_g * 9) / 4, 0)
    return {
        "protein_g": round(protein_g, 0),
        "fat_g": round(fat_g, 0),
        "carbs_g": round(carbs_g, 0),
    }


def hydration_target(weight_kg: float, workout_minutes: Optional[int] = None) -> Dict[str, Any]:
    liters = weight_kg * 0.033
    if workout_minutes:
        liters += max(workout_minutes, 0) / 60 * 0.5
    return {"water_liters_per_day": round(liters, 1)}


EXERCISE_LIBRARY = {
    "push": ["Push-ups", "Dumbbell bench press", "Incline push-ups", "Shoulder press"],
    "pull": ["Rows", "Lat pulldown", "Pull-ups", "Face pulls"],
    "legs": ["Squats", "Romanian deadlifts", "Lunges", "Leg press"],
    "core": ["Plank", "Dead bug", "Hollow hold", "Reverse crunch"],
    "full body": ["Goblet squat", "Push-ups", "Rows", "Farmer carry"],
    "cardio": ["Brisk walk", "Cycling", "Rowing", "Jump rope"],
}


def generate_workout_plan(
    goal: str = "general fitness",
    experience: str = "beginner",
    days_per_week: int = 3,
    equipment: str = "bodyweight",
) -> Dict[str, Any]:
    goal_norm = _normalize(goal)
    exp = _normalize(experience)
    equipment_norm = _normalize(equipment)

    if days_per_week <= 2:
        split = ["full body"] * days_per_week
    elif days_per_week == 3:
        split = ["push", "pull", "legs"]
    elif days_per_week == 4:
        split = ["upper", "lower", "push", "pull"]
    else:
        split = ["push", "pull", "legs", "upper", "lower"][:days_per_week]

    sessions: List[Dict[str, Any]] = []
    for day_index, focus in enumerate(split, start=1):
        if focus == "upper":
            exercises = ["Push-ups", "Rows", "Shoulder press", "Bicep curls"]
        elif focus == "lower":
            exercises = ["Squats", "Romanian deadlifts", "Lunges", "Calf raises"]
        else:
            exercises = EXERCISE_LIBRARY.get(focus, EXERCISE_LIBRARY["full body"])

        if "home" in equipment_norm or "bodyweight" in equipment_norm:
            exercises = [e for e in exercises if e not in {"Dumbbell bench press", "Lat pulldown", "Leg press"}]
            if not exercises:
                exercises = ["Squats", "Push-ups", "Plank", "Brisk walk"]

        if exp == "beginner":
            sets, reps, rest = "2-3", "8-12", "60-90 sec"
        elif exp == "intermediate":
            sets, reps, rest = "3-4", "6-12", "60-120 sec"
        else:
            sets, reps, rest = "4-5", "3-8", "90-180 sec"

        sessions.append(
            {
                "day": day_index,
                "focus": focus.title(),
                "warm_up": ["5 min brisk walk", "joint circles", "dynamic mobility"],
                "main": [{"exercise": ex, "sets": sets, "reps": reps, "rest": rest} for ex in exercises[:4]],
                "cooldown": ["Light stretching", "1-2 min breathing reset"],
            }
        )

    weekly_notes = [
        "Add 1 rep per set each week before increasing load.",
        "Stop 1-2 reps before failure on most sets.",
        "Sleep 7-9 hours for recovery.",
    ]
    if "fat loss" in goal_norm or "loss" in goal_norm:
        weekly_notes.append("Keep 2-4 low-intensity cardio sessions of 20-30 min.")
    if "muscle" in goal_norm or "bulk" in goal_norm:
        weekly_notes.append("Prioritize progressive overload and enough protein.")

    return {
        "goal": goal,
        "experience": experience,
        "days_per_week": days_per_week,
        "equipment": equipment,
        "sessions": sessions,
        "weekly_notes": weekly_notes,
    }


def classify_intent(message: str) -> str:
    text = _normalize(message)
    if any(k in text for k in ["bmi", "weight status"]):
        return "bmi"
    if any(k in text for k in ["bmr", "tdee", "calorie", "calories", "macro", "macros", "protein", "diet"]):
        return "nutrition"
    if any(k in text for k in ["workout", "training plan", "gym plan", "exercise plan", "split", "routine"]):
        return "workout_plan"
    if any(k in text for k in ["injury", "pain", "hurt", "diagnosed", "medical"]):
        return "safety"
    return "general"
