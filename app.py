from flask import Flask, render_template, request, jsonify, session
import json
import random

from chatbot import get_response
from emotion_api import emotion_api

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.register_blueprint(emotion_api)

with open("intents.json") as f:
    intents = json.load(f)

def find_intent(tag):
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return intent
    return None

def handle_followup(user_input, followups):
    if not followups:
        return None, []

    current = followups[0]
    expected = current.get("expected_responses", {})
    user_input_lower = user_input.lower()

    # Flexible keyword match
    for key, val in expected.items():
        key_words = key.lower().split()
        if any(word in user_input_lower for word in key_words):
            return random.choice(val["responses"]), val.get("followups", [])

    # Proceed to next question if response is not empty
    if user_input_lower.strip():
        next_followups = followups[1:] if len(followups) > 1 else []
        if next_followups:
            return next_followups[0].get("question", "Could you clarify?"), next_followups
        else:
            return "Thank you for sharing. I'm here to listen.", []

    # Repeat question if empty input
    return current.get("question", "Could you clarify?"), followups

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_text = data.get("message", "").lower().strip()
    detected_emotion = data.get("emotion", None)
    followups = session.get("followup_stack", [])

    # 🎯 Academic stress override
    academic_keywords = ["exam", "grades", "marks", "study", "studies", "fail", "failed", "school", "test"]
    if any(word in user_text for word in academic_keywords):
        predicted_tag = "academic_stress"
        intent = find_intent(predicted_tag)
        response = random.choice(intent["responses"])
        session["last_intent"] = predicted_tag
        if "followups" in intent and intent["followups"]:
            followup_q = intent["followups"][0]["question"]
            session["followup_stack"] = intent["followups"]
            return jsonify({"response": response + " " + followup_q})
        return jsonify({"response": response})

    # 🆘 Suicide/crisis override
    crisis_keywords = ["i want to die", "kill myself", "end my life", "suicidal", "hurt myself"]
    if any(kw in user_text for kw in crisis_keywords):
        session["followup_stack"] = []
        return jsonify({
            "response": "💔 I'm really sorry you're feeling this way. You're not alone. Please talk to someone or call a helpline right away: 9152987821 (iCALL, India)."
        })

    # 🌟 Greeting override to avoid misclassification
    greeting_inputs = ["hi", "hello", "hey", "hi there", "hello there"]
    if user_text in greeting_inputs:
        session["followup_stack"] = []
        session["last_intent"] = "greeting"
        intent = find_intent("greeting")
        return jsonify({"response": random.choice(intent["responses"])})

    # 🎉 Reset follow-up if user says they feel better
    if "feel better" in user_text:
        session["followup_stack"] = []
        return jsonify({
            "response": "I'm really happy to hear that. Keep taking care of yourself! 🌟"
        })

    # 🔁 Continue follow-up conversation
    if followups:
        response, next_followups = handle_followup(user_text, followups)
        session["followup_stack"] = next_followups
        return jsonify({"response": response})

    # 🎯 Predict main intent
    predicted_tag, response = get_response({"text": user_text, "emotion": detected_emotion})
    last_tag = session.get("last_intent")
    if predicted_tag != last_tag:
        session["followup_stack"] = []
        session["last_intent"] = predicted_tag

    # Check for followups in the new intent
    intent = find_intent(predicted_tag)
    if intent:
        if "followups" in intent and intent["followups"]:
            followup_q = intent["followups"][0]["question"]
            session["followup_stack"] = intent["followups"]
            if response.strip().endswith(followup_q.strip()):
                return jsonify({"response": response})
            else:
                return jsonify({"response": response + " " + followup_q})
        session["followup_stack"] = []
        return jsonify({"response": response})

    session["followup_stack"] = []
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
