import threading
import time
import os
import shutil
from flask import Flask, render_template_string, request, jsonify, send_from_directory
import webview
from tkinter import Tk, filedialog

Tk().withdraw()

image_path = filedialog.askopenfilename(
    title="Select an image for Vission",
    filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.ico")]
)

if not os.path.exists("static"):
    os.makedirs("static")

if image_path:
    shutil.copy(image_path, os.path.join("static", "myphoto.jpg"))
    shutil.copy(image_path, os.path.join("static", "favicon.ico"))

app = Flask(__name__)

chat_messages = []

def ai_reply(user_message):
    user_message = user_message.lower()
    if "hello" in user_message:
        return "Hello! How can I help you today?"
    elif "problem" in user_message:
        return "Please describe your problem in detail so I can assist you."
    elif "thank" in user_message:
        return "You are welcome!"
    elif "internet" in user_message:
        return "Try restarting your router and checking your connection."
    elif "bye" in user_message:
        return "Goodbye! Have a great day!"
    else:
        return "I understand. But sorry for the inconvenience, our app is currently under development. Please wait a little longer and I will make sure all your problems are resolved."

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Vission</title>
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 500px;
            width: 90%;
        }
        h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        img {
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .btn {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: background 0.2s;
        }
        .btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Thanks for giving us a chance to solve your problem</h1>
        <img src="/static/myphoto.jpg" alt="Photo" style="margin:20px 0; max-width:100%; height:auto; max-height:250px;">
        <p><a href="/chat" class="btn">Click to Chat</a></p>
    </div>
</body>
</html>
"""

CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Vission - Chat</title>
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .chat-container {
            background: white;
            width: 90%;
            max-width: 600px;
            height: 80vh;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: #007bff;
            color: white;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
        .chat-box {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #fdfdfd;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message-row {
            display: flex;
            width: 100%;
        }
        .message-row.user {
            justify-content: flex-end;
        }
        .message-row.ai {
            justify-content: flex-start;
        }
        .bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 15px;
            line-height: 1.4;
            word-wrap: break-word;
        }
        .user .bubble {
            background: #007bff;
            color: white;
            border-bottom-right-radius: 2px;
        }
        .ai .bubble {
            background: #f1f3f4;
            color: #333;
            border-bottom-left-radius: 2px;
        }
        .chat-input-area {
            display: flex;
            padding: 15px;
            background: #fff;
            border-top: 1px solid #eee;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            outline: none;
            font-size: 15px;
        }
        input[type="text"]:focus {
            border-color: #007bff;
        }
        button {
            margin-left: 10px;
            padding: 0 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #0056b3;
        }
    </style>
    <script>
        async function sendMessage() {
            let msgInput = document.getElementById("msg");
            let msg = msgInput.value;
            if (msg.trim() !== "") {
                msgInput.value = "";
                await fetch("/send_message", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: msg})
                });
                loadMessages();
            }
        }

        async function loadMessages() {
            let res = await fetch("/get_messages");
            let messages = await res.json();
            let chatBox = document.getElementById("chatBox");
            chatBox.innerHTML = "";
            messages.forEach(m => {
                let roleClass = (m.sender === "You") ? "user" : "ai";
                chatBox.innerHTML += `
                    <div class="message-row ${roleClass}">
                        <div class="bubble">${m.text}</div>
                    </div>`;
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function checkEnter(event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        }

        setInterval(loadMessages, 1000);
    </script>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">Vission AI Assistant</div>
        <div id="chatBox" class="chat-box"></div>
        <div class="chat-input-area">
            <input type="text" id="msg" placeholder="Type your message..." onkeypress="checkEnter(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(INDEX_HTML)

@app.route("/chat")
def chat():
    return render_template_string(CHAT_HTML)

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    message = data.get("message", "").strip()
    if message:
        chat_messages.append({"sender": "You", "text": message})
        reply = ai_reply(message)
        chat_messages.append({"sender": "Vission AI", "text": reply})
    return jsonify({"status": "ok"})

@app.route("/get_messages")
def get_messages():
    return jsonify(chat_messages)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

def start_flask():
    app.run(debug=False, port=5000, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    time.sleep(1)
    webview.create_window("Vission", "http://127.0.0.1:5000", width=800, height=600)
    webview.start()
