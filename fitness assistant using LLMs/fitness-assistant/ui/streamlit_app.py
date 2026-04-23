from __future__ import annotations

import streamlit as st

from app.agent import respond
from app.schemas import UserProfile

st.set_page_config(page_title="FitForge AI", page_icon="🏋️", layout="wide")

st.title("FitForge AI")
st.caption("An AI fitness assistant for workout plans, calorie guidance, and healthy training advice.")

with st.sidebar:
    st.header("Your profile")
    age = st.number_input("Age", min_value=5, max_value=120, value=25, step=1)
    gender = st.selectbox("Gender", ["male", "female", "other"], index=0)
    weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=500.0, value=70.0, step=0.5)
    height_cm = st.number_input("Height (cm)", min_value=80.0, max_value=250.0, value=170.0, step=0.5)
    activity_level = st.selectbox("Activity level", ["sedentary", "light", "moderate", "active", "very active"], index=2)
    goal = st.selectbox("Goal", ["maintenance", "fat loss", "muscle gain", "general fitness"], index=1)
    workouts_per_week = st.slider("Workouts per week", 1, 7, 4)
    equipment = st.selectbox("Equipment", ["bodyweight", "dumbbells", "full gym", "home gym"], index=0)
    diet_pref = st.text_input("Diet preference", placeholder="optional")
    use_profile = st.checkbox("Use my profile in responses", value=True)

profile = UserProfile(
    age=int(age),
    gender=gender,
    weight_kg=float(weight_kg),
    height_cm=float(height_cm),
    activity_level=activity_level,
    goal=goal,
    workouts_per_week=int(workouts_per_week),
    equipment=equipment,
    diet_pref=diet_pref or None,
) if use_profile else None

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_message = st.chat_input("Ask me for a workout plan, calorie target, macros, or training advice...")

if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = respond(user_message, profile=profile, history=st.session_state.messages)
            reply = result["reply"]
            st.markdown(reply)
            if result.get("tool_used"):
                with st.expander("Tool output"):
                    st.json(result.get("tool_result"))
    st.session_state.messages.append({"role": "assistant", "content": reply})
