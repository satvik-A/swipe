from tools import query_groq

print("🎁 Welcome to Slash – Your AI Gifting Concierge!")
print("Let's find the perfect experience gift for you. Answer a few short questions...\n")

messages = [{
    "role": "system",
    "content": "You are an AI concierge helping users find the perfect experience gift from a database. Ask one gift-relevant question at a time based on previous answers. Keep it conversational, short, and focused on personalizing the recommendation."
}]

quiz_answers = {}

# Start the quiz
initial_question = query_groq(messages)
print("Q1:", initial_question)
answer = input("> ")
quiz_answers["q1"] = answer
messages.append({"role": "user", "content": answer})

# Ask 4 more dynamic questions
for i in range(2, 6):
    followup_question = query_groq(messages)
    print(f"Q{i}:", followup_question)
    user_reply = input("> ")
    quiz_answers[f"q{i}"] = user_reply
    messages.append({"role": "user", "content": user_reply})

print("\nThanks! Let me find the best experience gift for you...\n")

# Final summarizing prompt to get recommendations
final_prompt = f"""
Based on the following answers:
{quiz_answers}

Suggest 3 personalized experience gifts for the user using only what you know from the answers. Keep suggestions practical and relevant for a gifting platform in India.
"""

messages.append({"role": "user", "content": final_prompt})

try:
    response = query_groq(messages)
    print("🎁 AI Recommendation:\n", response)
except Exception as e:
    print("Error:", e)