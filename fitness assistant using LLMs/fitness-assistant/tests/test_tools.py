from app.tools import calculate_bmi, calculate_bmr, calculate_tdee, generate_workout_plan


def test_bmi_category():
    result = calculate_bmi(70, 175)
    assert result["category"] == "Normal"


def test_bmr_and_tdee():
    bmr = calculate_bmr(70, 175, 25, "male")
    tdee = calculate_tdee(bmr["bmr"], "moderate")
    assert bmr["bmr"] > 0
    assert tdee["tdee"] > bmr["bmr"]


def test_workout_plan_days():
    plan = generate_workout_plan(goal="fat loss", experience="beginner", days_per_week=4, equipment="bodyweight")
    assert len(plan["sessions"]) == 4
