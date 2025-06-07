from tools import query_groq

recipient_context = {}

def ask_and_respond(question, prev_q=None, prev_a=None):
    if prev_q and prev_a:
        print(f"Got it — for '{prev_q}', you said: {prev_a}.")
    answer = input(f"{question}\n> ")

    # Store context
    key = question.split(".")[1].strip().lower().replace(" ", "_")
    recipient_context[key] = answer

    # AI comment on the answer if needed
    context_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in recipient_context.items()])
    prompt = f"You are helping someone choose a gift experience. Here's what you know so far:\n{context_summary}\nRespond briefly and conversationally to their answer: '{answer}'"
    messages = [{"role": "user", "content": prompt}]
    try:
        ai_response = query_groq(messages)
        print(f"🤖 {ai_response}\n")
    except Exception as e:
        print("❌ AI Error:", e)

    return question, answer

def collect_gift_info():
    questions = [
        "1. What is your relationship to the recipient?",
        "2. What is the occasion for the gift?",
        "3. What best describes them? (e.g. adventurous, calm, foodie, creative, etc.)",
        "4. What is your budget for this occasion?",
        "5. Where would you like the experience to take place (location)?"
    ]
    answers = []
    prev_q = prev_a = None
    for q in questions:
        qa = ask_and_respond(q, prev_q, prev_a)
        answers.append(qa)
        prev_q, prev_a = qa
    return answers

def format_final_prompt():
    prompt = "You are a creative and thoughtful assistant helping someone choose a unique experience gift. Based on the following details, suggest one highly relevant experience with a short reason:\n\n"
    for key, value in recipient_context.items():
        prompt += f"{key.replace('_', ' ').capitalize()}: {value}\n"
    prompt += "\nKeep it concise but vivid."
    return prompt

def follow_up_chat():
    print("🗨️ You can now ask any follow-up questions about the gift or recipient. Type 'exit' to end.")
    while True:
        user_q = input("> ")
        if user_q.strip().lower() in ["exit", "quit"]:
            print("👋 Thanks for using the gifting assistant. Happy gifting!")
            break
        # Add context memory
        context = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in recipient_context.items()])
        messages = [{"role": "user", "content": f"Here is what we know about the recipient:\n{context}\nUser question: {user_q}"}]
        try:
            answer = query_groq(messages)
            print("🤖", answer)
        except Exception as e:
            print("❌ Error:", e)

if __name__ == "__main__":
    print("🎁 Welcome to the Experience Gifting Assistant!\nI'll ask a few quick questions to help you find the perfect gift.\n")

    _ = collect_gift_info()

    try:
        final_prompt = format_final_prompt()
        messages = [{"role": "user", "content": final_prompt}]
        suggestion = query_groq(messages)
        print("\n✨ Final Experience Recommendation:")
        print(suggestion)
    except Exception as e:
        print("❌ Error:", e)

    follow_up_chat()
