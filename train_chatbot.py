import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# Load intents
with open('intents.json') as f:
    intents = json.load(f)

# Prepare training data
X = []
y = []
for intent in intents['intents']:
    tag = intent['tag']
    for pattern in intent['patterns']:
        X.append(pattern)
        y.append(tag)

# Vectorize patterns
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# Train classifier
model = MultinomialNB()
model.fit(X_vec, y)

# Save model and vectorizer
with open('chatbot_model.pkl', 'wb') as f:
    pickle.dump((vectorizer, model, model.classes_), f)

print('Model trained and saved as chatbot_model.pkl')
