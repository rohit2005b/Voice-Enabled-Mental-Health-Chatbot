import json
import nltk
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from nltk.stem import WordNetLemmatizer

print("🔄 Downloading NLTK data...")
nltk.download('punkt')
nltk.download('wordnet')

print("📂 Loading intents...")
with open("intents.json", encoding="utf-8") as file:
    intents = json.load(file)

lemmatizer = WordNetLemmatizer()
corpus = []
tags = []

print("🧹 Preprocessing patterns...")
for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        tokens = nltk.word_tokenize(pattern)
        tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens]
        processed = " ".join(tokens)
        corpus.append(processed)
        tags.append(intent["tag"])

print("🔢 Vectorizing text...")
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

print("🤖 Training model...")
model = LogisticRegression()
model.fit(X, tags)

print("💾 Saving model to chatbot_model.pkl...")
with open("chatbot_model.pkl", "wb") as f:
    pickle.dump((vectorizer, model, list(set(tags))), f)

print("✅ Training complete!")
