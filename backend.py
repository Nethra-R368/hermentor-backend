import os
import json
import base64
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq

# ------------------------------------------
# LOAD ENV
# ------------------------------------------
load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")
FIREBASE_ACC = os.getenv("FIREBASE_SERVICE_ACCOUNT")

client = Groq(api_key=GROQ_KEY)
MODEL = "llama-3.3-70b-versatile"

# ------------------------------------------
# FLASK
# ------------------------------------------
app = Flask(__name__)
CORS(app)

# ------------------------------------------
# GLOBAL ERROR HANDLER
# ------------------------------------------
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500


# ------------------------------------------
# FIREBASE
# ------------------------------------------
if FIREBASE_ACC:
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_ACC)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    db = None


# ------------------------------------------
# JSON SANITIZER (THE MAGIC FIX)
# ------------------------------------------
def extract_json(text):
    """Extract JSON object safely from AI output."""
    try:
        match = re.search(r"\{.*\}", text.strip(), re.DOTALL)
        if match:
            clean = match.group(0)
            return json.loads(clean)
        return {"error": "No JSON found in response", "raw": text}
    except:
        return {"error": "Failed to parse JSON", "raw": text}


# ------------------------------------------
# AI HELPERS
# ------------------------------------------
def ai_text(prompt):
    """Plain natural-language output."""
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Error: {str(e)}"


def ai_json(prompt):
    """Force structured JSON output with sanitization."""
    try:
        res = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        raw = res.choices[0].message.content.strip()
        return extract_json(raw)
    except Exception as e:
        return {"error": "json_parse_failed", "details": str(e)}


# ------------------------------------------
# BADGE MEMORY
# ------------------------------------------
user_badges = {}

def award_badge(uid, badge):
    if uid not in user_badges:
        user_badges[uid] = []
    if badge not in user_badges[uid]:
        user_badges[uid].append(badge)


# ------------------------------------------
# ROUTES
# ------------------------------------------
@app.route("/")
def home():
    return jsonify({"status": "backend running"})


# ------------------------------------------
# CREATE USER
# ------------------------------------------
@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.json
    uid = data.get("user_id")

    if not uid:
        return jsonify({"error": "Missing user_id"}), 400

    if db:
        db.collection("users").document(uid).set(data, merge=True)

    return jsonify({"success": True})


# ------------------------------------------
# SKILL ASSESSMENT
# ------------------------------------------
@app.route("/assess_skills", methods=["POST"])
def assess_skills():
    text = request.json.get("resume_text", "")

    prompt = f"""
    Analyze the following resume text and return structured JSON.

    Resume:
    {text}

    Return EXACTLY:
    {{
      "summary": "",
      "strengths": [],
      "weaknesses": [],
      "missing_skills": [],
      "recommended_courses": [],
      "project_ideas": [],
      "job_roles_now": [],
      "future_opportunities": [],
      "next_5_steps": []
    }}
    """

    return jsonify(ai_json(prompt))


# ------------------------------------------
# ROLE MODELS
# ------------------------------------------
@app.route("/role_models", methods=["GET"])
def role_models():
    prompt = """
    Return JSON:
    {
      "role_models": [
        {"name":"...", "field":"...", "bio":"..."}
      ]
    }
    Generate 5 inspiring women in STEM.
    """
    return jsonify(ai_json(prompt))


# ------------------------------------------
# MENTOR TEXT CHAT
# ------------------------------------------
@app.route("/mentor_chat", methods=["POST"])
def mentor_chat():
    msg = request.json.get("message", "")

    prompt = f"""
    You are ARIA — a warm, big-sister mentor.
    Encourage, motivate, and speak kindly.

    User: {msg}
    """

    reply = ai_text(prompt)
    return jsonify({"reply": reply})


# ------------------------------------------
# MENTOR VOICE CHAT
# ------------------------------------------
@app.route("/mentor_voice", methods=["POST"])
def mentor_voice():
    msg = request.json.get("message", "")

    prompt = f"""
    You are ARIA — soft, warm and comforting.
    User said:
    {msg}
    """

    text_reply = ai_text(prompt)

    try:
        tts = client.audio.speech.create(
            model="whisper-large-v3",
            voice="default",
            input=text_reply
        )
        audio_b64 = base64.b64encode(tts.audio).decode("utf-8")

        return jsonify({
            "reply": text_reply,
            "audio_base64": audio_b64
        })

    except Exception as e:
        return jsonify({"error": str(e), "reply": text_reply})


# ------------------------------------------
# QUIZ GENERATOR
# ------------------------------------------
@app.route("/generate_quiz", methods=["POST"])
def quiz():
    topic = request.json.get("topic", "")

    prompt = f"""
    Create a JSON quiz on {topic}.
    Return:
    {{
      "quiz": [
        {{
          "question": "",
          "options": ["A","B","C","D"],
          "answer": ""
        }}
      ]
    }}
    """

    return jsonify(ai_json(prompt))


# ------------------------------------------
# ROADMAP GENERATOR (THIS WAS THE BUG)
# ------------------------------------------
@app.route("/generate_roadmap", methods=["POST"])
def roadmap():
    goal = request.json.get("goal", "")
    hours = request.json.get("hours", 10)

    prompt = f"""
    Create a 4-week learning roadmap to become a {goal}.
    Study time: {hours} hours/week.

    Return EXACT JSON:
    {{
      "roadmap": [
        {{
          "week": 1,
          "topics": [],
          "tasks": [],
          "resources": []
        }},
        {{
          "week": 2,
          "topics": [],
          "tasks": [],
          "resources": []
        }},
        {{
          "week": 3,
          "topics": [],
          "tasks": [],
          "resources": []
        }},
        {{
          "week": 4,
          "topics": [],
          "tasks": [],
          "resources": []
        }}
      ]
    }}
    """

    return jsonify(ai_json(prompt))


# ------------------------------------------
# BADGES
# ------------------------------------------
@app.route("/award_badge", methods=["POST"])
def give_badge():
    uid = request.json.get("user_id")
    badge = request.json.get("badge")

    if not uid or not badge:
        return jsonify({"error": "Missing fields"}), 400

    award_badge(uid, badge)

    return jsonify({"success": True, "badges": user_badges[uid]})


@app.route("/get_badges/<uid>", methods=["GET"])
def get_badge(uid):
    return jsonify({"badges": user_badges.get(uid, [])})


# ------------------------------------------
# RUN SERVER
# ------------------------------------------
if __name__ == "__main__":
    app.run(port=8000, debug=True)
