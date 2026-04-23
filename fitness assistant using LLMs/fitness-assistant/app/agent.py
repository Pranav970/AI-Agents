from __future__ import annotations

from typing import Any, Dict, Optional

from app.llm import LLMClient
from app.prompts import SYSTEM_PROMPT, WORKOUT_STYLE_GUIDE
from app.schemas import UserProfile
from app.tools import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calorie_target,
    classify_intent,
    generate_workout_plan,
    hydration_target,
    macro_split,
)


def _profile_summary(profile: Optional[UserProfile]) -> str:
    if not profile:
        return "No profile provided."
    data = profile.model_dump(exclude_none=True)
    return "User profile: " + ", ".join(f"{k}={v}" for k, v in data.items())


def _extract_goal_hint(message: str) -> str:
    text = message.lower()
    if any(k in text for k in ["fat loss", "lose", "cut", "reduce"]):
        return "fat loss"
    if any(k in text for k in ["muscle", "bulk", "gain", "mass"]):
        return "muscle gain"
    return "general fitness"


def _safe_int(value: Optional[int], fallback: int) -> int:
    return value if isinstance(value, int) and value > 0 else fallback


def _compose_workout_reply(tool: Dict[str, Any], goal: str) -> str:
    sessions = tool["sessions"]
    lines = [
        f"Here is a {tool['days_per_week']}-day workout plan for {goal}:",
        "",
    ]
    for session in sessions:
        lines.append(f"Day {session['day']} — {session['focus']}")
        lines.append("Warm-up: " + ", ".join(session["warm_up"]))
        lines.append("Main work:")
        for ex in session["main"]:
            lines.append(f"- {ex['exercise']}: {ex['sets']} sets x {ex['reps']} | rest {ex['rest']}")
        lines.append("Cooldown: " + ", ".join(session["cooldown"]))
        lines.append("")
    lines.append("Weekly notes:")
    for note in tool["weekly_notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines)


def _compose_nutrition_reply(profile: Optional[UserProfile]) -> str:
    if not profile or not profile.weight_kg or not profile.height_cm or not profile.age:
        return (
            "To calculate calories and macros accurately, I need your age, weight, height, and goal. "
            "Share those and I will build a personalized plan."
        )

    bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
    bmr = calculate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
    tdee = calculate_tdee(bmr["bmr"], profile.activity_level or "moderate")
    calories = calorie_target(tdee["tdee"], profile.goal or "maintenance")
    macros = macro_split(calories["calories_per_day"], weight_kg=profile.weight_kg)
    hydration = hydration_target(profile.weight_kg)

    return (
        f"Your BMI is {bmi['bmi']} ({bmi['category']}).\n"
        f"Estimated BMR: {bmr['bmr']} kcal/day.\n"
        f"Estimated TDEE: {tdee['tdee']} kcal/day.\n"
        f"Suggested target: {calories['calories_per_day']} kcal/day for {calories['mode']}.\n\n"
        f"Macro guide:\n"
        f"- Protein: {macros['protein_g']} g/day\n"
        f"- Fat: {macros['fat_g']} g/day\n"
        f"- Carbs: {macros['carbs_g']} g/day\n\n"
        f"Hydration target: about {hydration['water_liters_per_day']} L/day.\n"
    )


def respond(message: str, profile: Optional[UserProfile] = None, history: Optional[list] = None) -> Dict[str, Any]:
    intent = classify_intent(message)
    llm = LLMClient()
    tool_used = None
    tool_result: Optional[Dict[str, Any]] = None

    days = _safe_int(profile.workouts_per_week if profile else None, 3)
    goal = profile.goal if profile and profile.goal else _extract_goal_hint(message)
    equipment = profile.equipment if profile and profile.equipment else "bodyweight"
    experience = "beginner"
    if profile and profile.activity_level:
        activity = profile.activity_level.lower()
        if activity in {"active", "very active"}:
            experience = "intermediate"

    if intent == "bmi" and profile and profile.weight_kg and profile.height_cm:
        tool_used = "calculate_bmi"
        tool_result = calculate_bmi(profile.weight_kg, profile.height_cm)
        reply = f"Your BMI is {tool_result['bmi']} and falls in the {tool_result['category']} category."

    elif intent == "nutrition":
        tool_used = "nutrition_calculator"
        if profile and profile.weight_kg and profile.height_cm and profile.age:
            bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
            bmr = calculate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
            tdee = calculate_tdee(bmr["bmr"], profile.activity_level or "moderate")
            target = calorie_target(tdee["tdee"], profile.goal or "maintenance")
            tool_result = {
                "bmi": bmi,
                "bmr": bmr,
                "tdee": tdee,
                "target": target,
                "macros": macro_split(target["calories_per_day"], weight_kg=profile.weight_kg),
                "hydration": hydration_target(profile.weight_kg),
            }
            reply = _compose_nutrition_reply(profile)
        else:
            reply = _compose_nutrition_reply(profile)

    elif intent == "workout_plan":
        tool_used = "generate_workout_plan"
        tool_result = generate_workout_plan(
            goal=goal,
            experience=experience,
            days_per_week=days,
            equipment=equipment,
        )
        reply = _compose_workout_reply(tool_result, goal)

    elif intent == "safety":
        reply = (
            "I can help with general fitness guidance, but for pain, injury, fainting, chest pain, "
            "or any medical concern, please stop training and get checked by a qualified clinician."
        )

    else:
        reply = (
            "Tell me your goal, age, weight, height, activity level, equipment, and training days, "
            "and I will build a workout and nutrition plan."
        )

    extra_context = "\n".join(
        [
            _profile_summary(profile),
            f"Intent: {intent}",
            f"Tool used: {tool_used or 'none'}",
            f"Workout style: {WORKOUT_STYLE_GUIDE}",
        ]
    )

    if llm.available() and intent in {"general", "workout_plan", "nutrition"}:
        try:
            llm_reply = llm.generate(
                system=SYSTEM_PROMPT,
                user=message,
                extra_context=f"{extra_context}\n\nTool result: {tool_result}" if tool_result else extra_context,
            )
            if llm_reply:
                reply = llm_reply
        except Exception:
            pass

    return {
        "reply": reply,
        "intent": intent,
        "tool_used": tool_used,
        "tool_result": tool_result,
    }
