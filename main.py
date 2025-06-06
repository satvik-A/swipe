from tools import query_groq

# user_prompt = input("enter your Q")
# # user_prompt = "give me all the topics in dsa"  # place holder for input 
# response = query_groq(user_prompt)
# print("AI:", response)

print("Welcome to the AI assistant. Type 'exit' to quit.")

messages = []

while True:
    user_prompt = input("Ask a question: ")
    if user_prompt.lower() == "exit":
        break
    messages.append({"role": "user", "content": user_prompt})
    try:
        response = query_groq(messages)
        print("AI:", response)
        messages.append({"role": "assistant", "content": response})
    except Exception as e:
        print("Error:", e)