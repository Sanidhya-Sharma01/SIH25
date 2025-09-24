import os
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from flask import Flask, request, jsonify, render_template_string
import webbrowser

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyDrAw15-Woz-qAvv6T9Eld9YNtSa0vjfQM"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize LangChain components with memory buffer
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Memory buffer to remember last 3 conversations (k=3)
memory = ConversationBufferWindowMemory(k=3, return_messages=True)

# Conversation chain with memory
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=False
)

def is_disaster_related(query: str) -> bool:
    disaster_keywords = [
        "earthquake", "flood", "tsunami", "disaster", "cyclone",
        "landslide", "natural calamity", "emergency", "first aid",
        "evacuation", "fire", "drought", "volcano", "hurricane",
        "typhoon", "pandemic", "epidemic", "rescue", "disaster relief",
        "safety", "preparedness", "alert", "storm", "aftershock", "evacuate",
        "natural hazard", "seismic", "aftershocks", "contingency", "disaster response",
        "aid", "relief", "response team", "shelter", "survival kit", "emergency bag",
        "warning", "natural event", "climate disaster", "flash flood", "wildfire",
        "heatwave", "tornado", "mudslide", "disaster zone"
    ]
    query = query.lower()
    return any(keyword in query for keyword in disaster_keywords)

# HTML Template embedded in the Python file
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aegis AI Chatbot Widget</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        
        #chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 300px;
            height: 40px;
            background: #007BFF;
            border-radius: 20px;
            color: white;
            cursor: pointer;
            transition: height 0.3s ease;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            overflow: hidden;
            display: flex;
            align-items: center;
            padding-left: 10px;
            z-index: 1000;
        }
        
        #chat-widget.open {
            height: 450px;
            flex-direction: column;
            padding: 10px;
            cursor: default;
        }
        
        #chat-icon {
            width: 30px;
            height: 30px;
            background: white;
            border-radius: 50%;
            margin-right: 12px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #007BFF;
        }
        
        #chat-title {
            font-weight: bold;
            font-size: 16px;
            user-select: none;
        }
        
        #chat-content {
            margin-top: 10px;
            flex-grow: 1;
            width: 100%;
            display: none;
            flex-direction: column;
            overflow-y: auto;
            background-color: #f9f9f9;
            color: #333;
            border-radius: 10px;
            padding: 10px;
            box-sizing: border-box;
        }
        
        #chat-widget.open #chat-content {
            display: flex;
        }
        
        .memory-indicator {
            font-size: 10px;
            color: #666;
            text-align: center;
            margin-bottom: 8px;
            padding: 3px;
            background-color: #e8f4ff;
            border-radius: 5px;
        }
        
        #message-area {
            flex-grow: 1;
            overflow-y: auto;
            margin-bottom: 10px;
            max-height: 300px;
            padding: 5px;
        }
        
        .message {
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 8px;
            max-width: 85%;
            word-wrap: break-word;
            line-height: 1.4;
            font-size: 14px;
        }
        
        .bot-message {
            background-color: #007BFF;
            color: white;
            align-self: flex-start;
            margin-right: auto;
        }
        
        .user-message {
            background-color: #d1e7dd;
            color: #0f5132;
            align-self: flex-end;
            margin-left: auto;
        }
        
        .loading-message {
            background-color: #ffeaa7;
            color: #d63031;
            font-style: italic;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        #user-input {
            display: flex;
            gap: 8px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
        }
        
        #user-input input {
            flex-grow: 1;
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #ccc;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        
        #user-input input:focus {
            border-color: #007BFF;
        }
        
        #user-input button {
            background-color: #007BFF;
            border: none;
            color: white;
            padding: 10px 16px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        
        #user-input button:hover:not(:disabled) {
            background-color: #0056b3;
        }
        
        #user-input button:disabled {
            background-color: #aac9f9;
            cursor: not-allowed;
        }
        
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f1aeb5;
            margin-bottom: 8px;
        }
        
        /* Scrollbar styling */
        #message-area::-webkit-scrollbar {
            width: 4px;
        }
        
        #message-area::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 2px;
        }
        
        #message-area::-webkit-scrollbar-thumb {
            background: #007BFF;
            border-radius: 2px;
        }
        
        #message-area::-webkit-scrollbar-thumb:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div id="chat-widget">
        <div id="chat-icon">🤖</div>
        <div id="chat-title">aegis ai</div>
        <div id="chat-content">
            <div class="memory-indicator">💭 Remembers last 3 conversations</div>
            <div id="message-area">
                <div class="message bot-message">Hello, I'm Aegis chat bot.</div>
                <div class="message bot-message">Ask questions related to disaster only.</div>
                <div class="message bot-message">Type 'exit' to quit.</div>
            </div>
            <form id="user-input" onsubmit="sendMessage(event)">
                <input type="text" id="input-box" autocomplete="off" placeholder="Type your disaster-related question..." required />
                <button type="submit" id="send-btn">Send</button>
            </form>
        </div>
    </div>

    <script>
        const widget = document.getElementById('chat-widget');
        const messageArea = document.getElementById('message-area');
        const inputBox = document.getElementById('input-box');
        const sendBtn = document.getElementById('send-btn');

        widget.addEventListener('click', () => {
            if (!widget.classList.contains('open')) {
                widget.classList.add('open');
                setTimeout(() => inputBox.focus(), 300);
            }
        });

        function appendMessage(text, sender, isLoading = false) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            
            if (sender === 'bot') messageDiv.classList.add('bot-message');
            else if (sender === 'user') messageDiv.classList.add('user-message');
            else if (sender === 'error') messageDiv.classList.add('error-message');
            
            if (isLoading) messageDiv.classList.add('loading-message');
            
            messageDiv.textContent = text;
            messageArea.appendChild(messageDiv);
            messageArea.scrollTop = messageArea.scrollHeight;
            
            return messageDiv;
        }

        async function sendMessage(event) {
            event.preventDefault();
            const userText = inputBox.value.trim();
            if (!userText) return;

            inputBox.disabled = true;
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';

            appendMessage(userText, 'user');
            inputBox.value = '';

            if (userText.toLowerCase() === 'exit') {
                appendMessage('Goodbye! Stay safe.', 'bot');
                inputBox.disabled = true;
                sendBtn.textContent = 'Chat Ended';
                return;
            }

            const loadingMsg = appendMessage('Thinking...', 'bot', true);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: userText })
                });
                
                const data = await response.json();
                loadingMsg.remove();
                appendMessage(data.response, 'bot');
                
            } catch (error) {
                loadingMsg.remove();
                appendMessage('Sorry, I encountered an error. Please try again.', 'error');
            } finally {
                inputBox.disabled = false;
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                inputBox.focus();
            }
        }

        inputBox.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage(event);
            }
        });
    </script>
</body>
</html>
"""

# Flask routes
@app.route('/')
def home():
    """Serve the main page with embedded HTML"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        
        if not user_input:
            return jsonify({'error': 'Empty message'}), 400
            
        if not is_disaster_related(user_input):
            return jsonify({
                'response': "I'm only trained to assist with disaster-related topics.",
                'is_disaster_related': False
            })
        
        prompt = f"""You are Aegis Bot, a disaster awareness assistant. Answer ONLY disaster-related questions.
        
        Instructions:
        - Answer in short bullet points (6-10 points max)
        - Each bullet point should be under 10 words
        - Keep total answer under 100 words
        - No paragraphs, headings, or long explanations
        
        Question: {user_input}"""
        
        response = conversation.predict(input=prompt)
        
        return jsonify({
            'response': response.strip(),
            'is_disaster_related': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory', methods=['GET'])
def get_memory():
    """Get current conversation memory"""
    try:
        memory_variables = memory.load_memory_variables({})
        return jsonify({'memory': str(memory_variables)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_memory', methods=['POST'])
def clear_memory():
    """Clear conversation memory"""
    try:
        memory.clear()
        return jsonify({'message': 'Memory cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🤖 Aegis Bot - Disaster Awareness Assistant with Memory")
    print("📝 Memory Buffer: Remembers last 3 conversations")
    print("🚀 Server starting on http://localhost:5000")
    print("💻 Open http://localhost:5000 in your browser")
    webbrowser.open("http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
