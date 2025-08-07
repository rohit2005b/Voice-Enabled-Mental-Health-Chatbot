// --- EMOTION DETECTION ---
let emotionInterval = null;
let lastDetectedEmotion = null;
function startEmotionDetection() {
  if (emotionInterval) return;
  emotionInterval = setInterval(captureAndSendFrame, 2000); // every 2 seconds
}

function stopEmotionDetection() {
  if (emotionInterval) clearInterval(emotionInterval);
  emotionInterval = null;
}

function captureAndSendFrame() {
  const video = document.getElementById('webcam');
  if (!video || video.readyState !== 4) return;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const dataURL = canvas.toDataURL('image/jpeg');
  fetch('/detect_emotion', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: dataURL })
  })
    .then(res => res.json())
    .then(data => {
      const emotionDiv = document.getElementById('emotion-result');
      if (data.emotion) {
        emotionDiv.textContent = 'Detected Emotion: ' + data.emotion;
        lastDetectedEmotion = data.emotion;
      } else {
        emotionDiv.textContent = 'Emotion not detected';
        lastDetectedEmotion = null;
      }
    })
    .catch(() => {
      const emotionDiv = document.getElementById('emotion-result');
      emotionDiv.textContent = 'Emotion detection error';
      lastDetectedEmotion = null;
    });
}
// ✅ Final working script.js with native speech output (no API needed)

function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value.trim();
  if (!message) return;

  displayMessage("You", message);
  input.value = "";

  fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: message, emotion: lastDetectedEmotion }),
  })
    .then((res) => res.json())
    .then((data) => {
      let botMsg = data.response;
      if (lastDetectedEmotion) {
        botMsg += `<br><span style='font-size:0.9em;color:#888;'>[Detected Emotion: ${lastDetectedEmotion}]</span>`;
      }
      displayMessage("Bot", botMsg);
      // Native speech synthesis
      const synth = window.speechSynthesis;
      const utterance = new SpeechSynthesisUtterance(data.response);
      utterance.lang = "en-US";
      synth.speak(utterance);
    });
}

function displayMessage(sender, text) {
  const chatbox = document.getElementById("chatbox");
  const msg = document.createElement("p");
  msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatbox.appendChild(msg);
  // Scroll to bottom smoothly
  chatbox.scrollTo({ top: chatbox.scrollHeight, behavior: "smooth" });
}

function startRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.start();

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById("userInput").value = transcript;
    sendMessage();
  };

  recognition.onspeechend = function () {
    recognition.stop();
  };

  recognition.onerror = function (event) {
    alert("Mic error: " + event.error + "\nPlease speak clearly within 5 seconds.");
  };
}
function startCamera() {
  const video = document.getElementById("webcam");
  if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then(function (stream) {
        video.srcObject = stream;
        startEmotionDetection();
      })
      .catch(function (error) {
        alert("Camera error: " + error.message);
      });
  } else {
    alert("Webcam not supported in this browser.");
  }
}
