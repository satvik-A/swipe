from tools import query_groq

user_prompt = "Suggest 3 unique gifting experiences for a foodie in hyderabad under ₹1500"
response = query_groq(user_prompt)
print("AI:", response)