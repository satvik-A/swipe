from tools import query_groq

recipient_context = {}

def ask_and_respond(question, prev_q=None, prev_a=None):
    # Build a one-paragraph natural question based on recipient context
    context_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in recipient_context.items()])
     
    custom_prompt = (
        "You are a warm and creative assistant helping someone choose a thoughtful experience gift. "
        "You will rewrite the given question as a natural, engaging prompt for the user. "
        "IMPORTANT: Do NOT answer the question, do NOT add any explanations, introductions, or phrases like "
        "'Here's your rewritten prompt:' or 'That's a great question!'. "
        "Return ONLY the rewritten question prompt, with 30–45 words (2–3 sentences), based on the context below. "
        f"Original question: '{question}'\nContext:\n{context_summary}\n"
        "Make it concise, friendly, and conversational."
    )

    try:
        final_question = query_groq([{"role": "user", "content": custom_prompt}])
    except Exception as e:
        print("❌ AI Question Generation Error:", e)
        final_question = question  # fallback

    # Ask the generated paragraph-question
    answer = input(f"{final_question}\n> ")

    # Store context
    key = question.split(".")[1].strip().lower().replace(" ", "_")
    recipient_context[key] = answer

    # Generate a follow-up conversational comment
    context_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in recipient_context.items()])
    response_prompt = (
        f"You are helping someone choose a gift experience. Here's what you know so far:\n{context_summary}\n"
        f"Respond briefly and conversationally to their answer: '{answer}'"
    )
    messages = [{"role": "user", "content": response_prompt}]
    try:
        ai_response = query_groq(messages)
        print(f"🤖 {ai_response}\n")
    except Exception as e:
        print("❌ AI Error:", e)

    return question, answer

def collect_gift_info():
    questions = [
        "1. Tell me a bit about your relationship with the person you're gifting—are they a close friend, partner, sibling, or someone else?",
        "2. What's the special occasion or reason behind this gift—birthday, anniversary, celebration, or just a surprise?",
        "3. If you had to describe their vibe or personality in a few words—like adventurous, calm, creative, or foodie—what would you say?",
        "4. What’s the general budget you’re planning to spend on this experience gift?",
        "5. Is there a specific city or region you’d like the experience to take place in, or should it be something flexible or online?"
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
