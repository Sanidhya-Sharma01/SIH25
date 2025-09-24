import os
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"
#from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain

import langchain
GOOGLE_API_KEY = "AIzaSyDrAw15-Woz-qAvv6T9Eld9YNtSa0vjfQM"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
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

print(" Aegis Bot - Disaster Awareness Assistant")
print(" Ask your questions related to natural disasters or calamities.")
print(" Type 'exit' to quit.\n")


while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Aegis Bot: Goodbye! Stay safe.")
        break

    if is_disaster_related(user_input):
        try:
            prompt = (
                "Answer the following disaster-related question ONLY in short bullet points. "
                "Do NOT write paragraphs, headings, or explanations. "
                "Only output 6-10 bullet points, each under 10 words. "
                "Keep the total answer under 100 words.\n\n"
                f"Question: {user_input}"
            )
            response = model.generate_content(prompt)
            print("Aegis Bot:\n" + response.text.strip())
        except Exception as e:
            print("Aegis Bot: Sorry, something went wrong.\n", str(e))
    else:
        print("Aegis Bot: I'm only trained to assist with disaster-related topics.")
