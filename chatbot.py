import json
import pickle
import random
import nltk
from nltk.stem import WordNetLemmatizer

# Load model and vectorizer
with open("chatbot_model.pkl", "rb") as f:
    vectorizer, model, classes = pickle.load(f)

# Load intents
with open("intents.json") as f:
    intents = json.load(f)

lemmatizer = WordNetLemmatizer()
nltk.download('punkt')
nltk.download('wordnet')

# Global variables for conversation state
last_tag = None
last_followup = None

# Hardcoded greetings to avoid low-confidence misclassification
hardcoded_greetings = ["hi", "hello", "hey", "hello there", "hi there", "hey there"]

def get_response(user_input):
    global last_tag, last_followup

    # Tokenize and lemmatize input
    if isinstance(user_input, dict):
        text = user_input.get("text", "")
        detected_emotion = user_input.get("emotion", None)
    else:
        text = user_input
        detected_emotion = None

    tokens = nltk.word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(w.lower()) for w in tokens]
    processed_input = " ".join(lemmatized)

    # 🔹 STEP 1: Hardcoded greeting override
    if processed_input.lower() in hardcoded_greetings:
        greeting_intent = next((i for i in intents["intents"] if i["tag"] == "greeting"), None)
        last_tag = None
        last_followup = None
        return "greeting", random.choice(greeting_intent["responses"])

    # 🔹 STEP 2: Follow-up conversation handling
    if last_tag and last_followup:
        expected = last_followup.get("expected_responses", {})
        for key, val in expected.items():
            if key.lower() in processed_input:
                response = random.choice(val["responses"])
                # Advance to next followup if any
                intent_obj = next((i for i in intents["intents"] if i["tag"] == last_tag), None)
                if intent_obj and "followups" in intent_obj:
                    idx = intent_obj["followups"].index(last_followup)
                    if idx + 1 < len(intent_obj["followups"]):
                        last_followup = intent_obj["followups"][idx + 1]
                        return last_tag, last_followup["question"]
                # End of followups
                last_tag = None
                last_followup = None
                return last_tag, response
        return last_tag, last_followup["question"]

    # 🔹 STEP 3: Emotion-based override
    def emotion_override(detected_emotion):
        emotion_map = {
            "sad": "feeling_low",
            "depressed": "depressed",
            "angry": "stress",
            "fear": "anxiety",
            "disgust": "feeling_low",
            "happy": "greeting",
            "neutral": None
        }
        if detected_emotion:
            return emotion_map.get(detected_emotion.lower())
        return None

    # 🔹 STEP 4: Main intent detection
    tag_from_emotion = emotion_override(detected_emotion)
    if tag_from_emotion:
        intent = next((i for i in intents["intents"] if i["tag"] == tag_from_emotion), None)
        if intent:
            response = random.choice(intent["responses"])
            if "followups" in intent and intent["followups"]:
                last_tag = tag_from_emotion
                last_followup = intent["followups"][0]
                return last_tag, last_followup["question"]
            return tag_from_emotion, response

    # 🔹 STEP 5: Model prediction
    input_vec = vectorizer.transform([processed_input])
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(input_vec)[0]
        if max(probs) < 0.2:
            return "no_match", "I'm not sure I understand. Can you tell me more?"
        predicted_tag = classes[probs.argmax()]
    else:
        predicted_tag = model.predict(input_vec)[0]

    # 🔹 STEP 6: Generate final response
    for intent in intents["intents"]:
        if intent["tag"] == predicted_tag:
            response = random.choice(intent["responses"])

            # Crisis escalation
            if detected_emotion in ["sad", "depressed"] and predicted_tag in ["depressed", "crisis_suicidal", "feeling_low"]:
                response += "\nIf you're in distress, please reach out to a helpline or therapist."

            # Set followup if present
            if "followups" in intent and intent["followups"]:
                last_tag = predicted_tag
                last_followup = intent["followups"][0]
                return last_tag, last_followup["question"]

            return predicted_tag, response

    return "no_match", "I'm not sure I understand. Can you tell me more?"
