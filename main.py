from tools import query_groq

# user_prompt = input("enter your Q")
# # user_prompt = "give me all the topics in dsa"  # place holder for input 
# response = query_groq(user_prompt)
# print("AI:", response)

print("Let's find the perfect experience gift for you! Answer a few quick questions:")

messages = []
quiz_answers = {}

questions = [
    {"key": "relationship", "text": "Who are you gifting this experience to? (e.g., friend, partner, parent)"},
    {"key": "occasion", "text": "What's the occasion? (e.g., birthday, anniversary, graduation)"},
    {"key": "budget", "text": "What's your budget for this gift (in INR)?"},
    {"key": "location", "text": "Where should the experience take place? (e.g., Delhi, Goa, Bangalore)"},
]

for idx, q in enumerate(questions):
    user_answer = input(f"{q['text']}\n> ")
    quiz_answers[q["key"]] = user_answer
    messages.append({"role": "user", "content": user_answer})

    # Custom follow-up after budget
    if q["key"] == "budget":
        try:
            budget = int(user_answer)
            if budget < 1000:
                follow_up = "Got it — you're going for something budget-friendly! Prefer something chill or exciting?"
            elif budget <= 3000:
                follow_up = "Nice! Do you want something adventurous or relaxing?"
            else:
                follow_up = "Wow! Looking for something premium and luxurious?"
            follow_up_ans = input(follow_up + "\n> ")
            quiz_answers["vibe"] = follow_up_ans
            messages.append({"role": "user", "content": follow_up_ans})
        except ValueError:
            pass

print("\nThanks! Let me find the best experience gift for you...")

# Build prompt using quiz answers
prompt = f"""
Suggest 3 experience gifts for someone gifting to their {quiz_answers.get("relationship")}, for a {quiz_answers.get("occasion")}, located in {quiz_answers.get("location")}, with a budget of ₹{quiz_answers.get("budget")}, and the user prefers a vibe like "{quiz_answers.get("vibe", "surprise")}".
"""

messages.append({"role": "user", "content": prompt})

try:
    response = query_groq(messages)
    print("\n🎁 AI Recommendation:\n", response)
except Exception as e:
    print("Error:", e)
        
        # this is the working version with continuous chat