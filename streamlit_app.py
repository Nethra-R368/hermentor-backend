############################################################
# HerMentor — FINAL WORKING FRONTEND (Streamlit)
############################################################

import streamlit as st
import requests
import os
import json

# Backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------
st.set_page_config(
    page_title="HerMentor — AI Mentor for Women in STEM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------
# GLOBAL STYLES (FIX SIDEBAR + DARK-PINK THEME)
# ------------------------------------------------------
st.markdown("""
<style>

:root {
    --bg: #0f0f12;
    --panel: #141416;
    --accent: #ff4fa1;
    --accent-dark: #c2185b;
    --text: #f5f5f5;
    --muted: #bbbbbb;
    --card: #1a1a1d;
    --bubble-user: #0d6b5f;
    --bubble-mentor: #222;
}

/* MAIN BACKGROUND */
.stApp { background-color: var(--bg); color: var(--text); }

/* FIXED SIDEBAR */
[data-testid="stSidebar"] {
    background-color: var(--panel) !important;
    min-width: 300px !important;
    max-width: 300px !important;
    border-right: 1px solid #000;
}

/* Remove collapsing arrow */
button[kind="header"] { display: none !important; }

/* Hero container */
.hero {
    background: linear-gradient(90deg, rgba(255,79,161,.15), rgba(255,79,161,.05));
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 20px;
}

/* CARD */
.card {
    background: var(--card);
    padding: 16px;
    border-radius: 12px;
    margin: 12px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,.4);
}

/* CHAT BUBBLES */
.chat-user {
    background: linear-gradient(90deg, #09594a, #0d6b5f);
    padding: 12px 15px;
    border-radius: 12px;
    color: white;
    max-width: 80%;
    margin: 8px 0;
    white-space: pre-wrap;
}

.chat-mentor {
    background: #222;
    padding: 12px 15px;
    border-radius: 12px;
    color: var(--text);
    max-width: 80%;
    margin: 8px 0;
    white-space: pre-wrap;
}

/* BUTTONS */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border-radius: 8px;
    padding: 10px 18px;
    border: none;
}
.stButton > button:hover {
    background: var(--accent-dark) !important;
}

/* Titles */
h1, h2, h3 { color: var(--accent) !important; }

footer { text-align:center; margin-top:35px; color: var(--accent); }

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# SERVER HELPERS
# ------------------------------------------------------
def post_json(path, payload):
    try:
        url = f"{BACKEND_URL}{path}"
        res = requests.post(url, json=payload, timeout=60)

        # Try JSON safely
        try:
            return res.json()
        except:
            return {
                "error": "Invalid JSON from backend",
                "status_code": res.status_code,
                "raw": res.text
            }

    except Exception as e:
        return {"error": f"Request failed: {e}"}

def get_json(path):
    try:
        url = f"{BACKEND_URL}{path}"
        res = requests.get(url, timeout=60)

        try:
            return res.json()
        except:
            return {
                "error": "Invalid JSON from backend",
                "status_code": res.status_code,
                "raw": res.text
            }

    except Exception as e:
        return {"error": f"Request failed: {e}"}

# ------------------------------------------------------
# HERO
# ------------------------------------------------------
st.title("💖 Aria — AI Mentor for Women in STEM")



# ------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------
pages = [
    "🌸 Create Profile",
    "🧠 Skill Assessment",
    "🚀 Roadmap Builder",
    "📝 Smart Quiz",
    "🌟 Role Models",
    "💬 Mentor Chat"
]

choice = st.sidebar.selectbox("Navigation", pages)

# Make session states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []


# ----------------------------------------------------------
# 🌸 CREATE PROFILE
# ----------------------------------------------------------
if choice == "🌸 Create Profile":
    st.header("🌸 Create / Update Profile")

    user_id = st.text_input("User ID", "user123")
    interests = st.text_input("Interests (comma separated)", "AI, ML, Data Science")
    resume = st.text_area("Resume / Bio", height=220)

    if st.button("💾 Save Profile"):
        res = post_json("/create_user", {
            "user_id": user_id,
            "interests": interests,
            "resume": resume
        })
        if res.get("success"):
            st.success("Profile saved successfully!")
        else:
            st.error(res)


elif choice == "🧠 Skill Assessment":
    st.header("🧠 Skill Assessment")

    resume = st.text_area("Paste your resume", height=260)

    if st.button("🔍 Analyze Skills"):
        res = post_json("/assess_skills", {"resume_text": resume})

        if "error" in res:
            st.error(res["error"])
        else:
            st.subheader("📘 Detailed Skill Analysis")

            # Backend returns keys directly (summary, strengths, weaknesses...)
            analysis = res

            def render_section(title, items, icon="✨"):
                if not items:
                    return
                st.markdown(
                    f"<h3 style='color: var(--accent); margin-top:20px;'>{icon} {title}</h3>",
                    unsafe_allow_html=True
                )
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if isinstance(items, list):
                    for item in items:
                        st.markdown(f"- {item}")
                else:
                    st.markdown(items)
                st.markdown("</div>", unsafe_allow_html=True)

            render_section("Strengths", analysis.get("strengths"), "💪")
            render_section("Weaknesses / Gaps", analysis.get("weaknesses"), "⚠️")
            render_section("Missing Skills", analysis.get("missing_skills"), "❗")
            render_section("Recommended Courses", analysis.get("recommended_courses"), "📚")
            render_section("Project Ideas", analysis.get("project_ideas"), "💡")
            render_section("Roles You Qualify For", analysis.get("job_roles_now"), "🎯")
            render_section("Future Opportunities", analysis.get("future_opportunities"), "🚀")
            render_section("Next 5 Steps", analysis.get("next_5_steps"), "🌟")

# ----------------------------------------------------------
# 🚀 ROADMAP BUILDER
# ----------------------------------------------------------
elif choice == "🚀 Roadmap Builder":
    st.header("🚀 Learning Roadmap")

    goal = st.text_input("Target Role", "Data Scientist")
    hours = st.number_input("Hours per week", 1, 40, 10)

    if st.button("✨ Generate Roadmap"):
        res = post_json("/generate_roadmap", {"goal": goal, "hours": hours})
        roadmap = res.get("roadmap")

        if "error" in res:
            st.error(res["error"])
        elif isinstance(roadmap, list):
            for week in roadmap:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"## Week {week['week']}")
                st.write("📘 Topics:", week["topics"])
                st.write("📝 Tasks:", week["tasks"])
                st.write("🔗 Resources:", week["resources"])
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Unexpected response from backend.")


# ----------------------------------------------------------
# 📝 SMART QUIZ
# ----------------------------------------------------------
elif choice == "📝 Smart Quiz":
    st.header("📝 AI Quiz Generator")

    topic = st.text_input("Topic", "Python Basics")

    col1, col2 = st.columns(2)
    with col1:
        gen = st.button("📝 Generate Quiz")
    with col2:
        more = st.button("➕ More Questions")

    if gen:
        res = post_json("/generate_quiz", {"topic": topic})
        st.session_state.quiz_data = res.get("quiz", [])

    if more:
        res = post_json("/generate_quiz", {"topic": topic})
        extra = res.get("quiz", [])
        st.session_state.quiz_data.extend(extra)

    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### Q{i+1}. {q['question']}")
        for idx, opt in enumerate(q["options"]):
            st.write(f"- **{chr(65+idx)}** {opt}")
        st.write(f"🟩 **Answer: {q['answer']}**")
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------
# 🌟 ROLE MODELS
# ----------------------------------------------------------
elif choice == "🌟 Role Models":
    st.header("🌟 Inspiring Women in STEM")

    res = get_json("/role_models")
    models = res.get("role_models", [])

    for m in models:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### {m['name']}")
        st.write(f"**Field:** {m['field']}")
        st.write(m["bio"])
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------
# 💬 MENTOR CHAT (FIXED INPUT CLEARING)
# ----------------------------------------------------------
elif choice == "💬 Mentor Chat":
    st.header("💬 Chat with Aria!")

    # Initialize states
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""           # stores text
    if "clear_flag" not in st.session_state:
        st.session_state.clear_flag = False        # tells Streamlit to clear input

    # ---- CLEAR INPUT BEFORE DRAWING ----
    if st.session_state.clear_flag:
        st.session_state.chat_input = ""           # wipe text box
        st.session_state.clear_flag = False        # reset flag

    # Show chat bubbles
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-mentor'>{msg['content']}</div>", unsafe_allow_html=True)

    # ---- Chat Input Box ----
    user_msg = st.text_input("Type your message…", key="chat_input")

    # ---- Send Button ----
    if st.button("Send"):
        if user_msg.strip():
            # Send to backend
            res = post_json("/mentor_chat", {"message": user_msg})
            reply = res.get("reply", "No reply.")

            # Add to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_msg})
            st.session_state.chat_history.append({"role": "mentor", "content": reply})

            # CLEAR INPUT SAFELY
            st.session_state.clear_flag = True

            st.rerun()  # rerun AFTER clearing


# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<footer>💖 Built for women, by women in STEM.</footer>", unsafe_allow_html=True)
