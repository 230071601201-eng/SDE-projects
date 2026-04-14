from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------
# LOAD context.txt FILE
# -------------------------------
with open("context.txt", "r", encoding="utf-8") as f:
    context = f.read()

# -------------------------------
# SYSTEM MESSAGE (with injected context)
# -------------------------------
messages = [
    {
        "role": "system",
        "content": f"""
You are a SaaS Support Assistant.

Use ONLY the documentation below:
{context}

IMPORTANT FALLBACK RULE:
If the answer is not found in the documentation, respond exactly with:

"I’m sorry, I couldn’t find that information in the SaaS Hub documentation. Please contact support or rephrase your question."

Do not guess or make up answers.
"""
    }
]

# -------------------------------
# HISTORY TRIMMING CONFIG
# -------------------------------
MAX_MESSAGES = 12  # keeps system + last chat exchanges

# -------------------------------
# CHAT LOOP
# -------------------------------
while True:
    user_input = input("You: ")

    if user_input.lower() in ["quit", "exit", "bye"]:
        print("Bot: Goodbye 👋")
        break

    # Add user message
    messages.append({"role": "user", "content": user_input})

    # -------------------------------
    # 🔥 HISTORY TRIMMING LOGIC
    # -------------------------------
    system_message = messages[0]
    recent_messages = messages[-(MAX_MESSAGES - 1):]

    trimmed_messages = [system_message] + recent_messages

    # Call OpenAI API using trimmed history
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=trimmed_messages
    )

    # Extract response correctly
    reply = response.choices[0].message.content

    # Save assistant response (FULL history still stored locally)
    messages.append({"role": "assistant", "content": reply})

    print(f"Bot: {reply}")