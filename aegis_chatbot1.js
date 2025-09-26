const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const open = require('open').default;
require('dotenv').config();


const app = express();
const PORT = process.env.PORT || 5000;


app.use(express.json());
app.use(express.urlencoded({ extended: true }));


const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
if (!GOOGLE_API_KEY) {
    console.error("Error: GOOGLE_API_KEY environment variable not set.");
    process.exit(1);
}
const genAI = new GoogleGenerativeAI(GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });


let conversationMemory = [];


function isDisasterRelated(query) {
    const disasterKeywords = [
        "earthquake", "flood", "tsunami", "disaster", "cyclone",
        "landslide", "natural calamity", "emergency", "first aid",
        "evacuation", "fire", "drought", "volcano", "hurricane",
        "typhoon", "pandemic", "epidemic", "rescue", "disaster relief",
        "safety", "preparedness", "alert", "storm", "aftershock", "evacuate",
        "natural hazard", "seismic", "aftershocks", "contingency", "disaster response",
        "aid", "relief", "response team", "shelter", "survival kit", "emergency bag","hi",
        "warning", "natural event", "climate disaster", "flash flood", "wildfire","bye",
        "heatwave", "tornado", "mudslide", "disaster zone", "help","stuck", "trapped","SOS","hello"
    ];
    
    const lowercaseQuery = query.toLowerCase();
    return disasterKeywords.some(keyword => lowercaseQuery.includes(keyword));
}


function addToMemory(user, bot) {
    conversationMemory.push({ user, bot, timestamp: new Date() });
    if (conversationMemory.length > 3) {
        conversationMemory.shift(); 
    }
}


function getMemoryContext() {
    return conversationMemory
        .map(conv => `User: ${conv.user}\nBot: ${conv.bot}`)
        .join('\n\n');
}


const HTML_TEMPLATE = `
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
            background: #202223ff;
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
        
        #close-btn {
            display: none;
            position: absolute;
            top: 10px;
            right: 5px;
            
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #ff4757;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        }

        #chat-widget.open #close-btn {
            display: block;
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
            color: #060606ff;
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
            background-color: #504d4dff;
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
            background-color: #141415ff;
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
            border-color: #fd0623ff;
        }
        
        #user-input button {
            background-color: #303132ff;
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
        <button id="close-btn" onclick="closeChat()">&times;</button>
        <div id="chat-icon">🤖</div>
        <div id="chat-title">Aegis Ai </div>
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

        function closeChat() {
            widget.classList.remove('open');
        }

        widget.addEventListener('click', (event) => {
            if (!widget.classList.contains('open') && event.target.id !== 'close-btn') {
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
`;


// API Routes
app.get('/', (req, res) => {
    res.send(HTML_TEMPLATE);
});


app.post('/chat', async (req, res) => {
    try {
        const { message } = req.body;
        
        if (!message || !message.trim()) {
            return res.status(400).json({ error: 'Message cannot be empty' });
        }
        
        const userInput = message.trim();
        
        if (!isDisasterRelated(userInput)) {
            const response = "I'm only trained to assist with disaster-related topics.";
            addToMemory(userInput, response);
            return res.json({ response, is_disaster_related: false });
        }
        
        const memoryContext = getMemoryContext();
        const systemPrompt = `You are Aegis Bot, a disaster awareness assistant. Answer ONLY disaster-related questions.

Previous conversation context:  
${memoryContext}

FORMAT EACH RESPONSE LIKE THIS EXAMPLE:
- Move to higher ground
- Avoid floodwater  
- Turn off utilities
- Have emergency kit ready

STRICT RULES:
- Each bullet starts new line
- Use hyphen-space format: "- "  
- Maximum 10 words per bullet
- 6-10 bullets total
- Under 100 words total

Question: ${userInput}`;
        const result = await model.generateContent(systemPrompt);
        const botResponse = result.response.text().trim();
        
        addToMemory(userInput, botResponse);
        
        return res.json({
            response: botResponse,
            is_disaster_related: true
        });
        
    } catch (error) {
        console.error('Chat error:', error);
        return res.status(500).json({ 
            error: 'Sorry, I encountered an error. Please try again.',
            details: error.message 
        });
    }
});


app.get('/memory', (req, res) => {
    try {
        const memoryData = {
            conversations: conversationMemory,
            count: conversationMemory.length,
            last_updated: conversationMemory.length > 0 ? conversationMemory[conversationMemory.length - 1].timestamp : null
        };
        return res.json({ memory: memoryData });
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
});


app.post('/clear_memory', (req, res) => {
    try {
        const previousCount = conversationMemory.length;
        conversationMemory = [];
        return res.json({ 
            message: 'Memory cleared successfully',
            cleared_conversations: previousCount 
        });
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
});


app.listen(PORT, () => {
    console.log('🤖 Aegis Bot - Disaster Awareness Assistant with Memory');
    console.log('📝 Memory Buffer: Remembers last 3 conversations');
    console.log(`🚀 Server starting on http://localhost:${PORT}`);
    console.log('💻 Open http://localhost:${PORT} in your browser');
    
    setTimeout(() => {
        open(`http://localhost:${PORT}`);
    }, 1000);
});


process.on('SIGINT', () => {
    console.log('\n🔄 Shutting down Aegis AI gracefully...');
    console.log('🛡️  Stay safe and be prepared!');
    process.exit(0);
});
