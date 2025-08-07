
from flask import Blueprint, request, jsonify
from deepface import DeepFace
import cv2
import numpy as np
import base64

emotion_api = Blueprint('emotion_api', __name__)

@emotion_api.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    data = request.json
    img_data = data.get('image')

    if not img_data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Decode base64 image
        img_bytes = base64.b64decode(img_data.split(',')[1])
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Analyze emotion
        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)

        # If result is a list (common in latest DeepFace), use result[0]
        if isinstance(result, list):
            emotion = result[0]['dominant_emotion']
        else:
            emotion = result['dominant_emotion']

        return jsonify({'emotion': emotion})
    
    except Exception as e:
        return jsonify({'error': f"Emotion detection failed: {str(e)}"}), 500
