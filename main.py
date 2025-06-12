from tools import query_groq

from tools import query_groq
from dotenv import load_dotenv

import os
import csv
import openai
import uuid
from qdrant_client import QdrantClient
import nltk

# openai.api_type = "azure"
# openai.api_base = os.getenv("Azure_link")    # e.g., "https://YOUR-RESOURCE.openai.azure.com/"
# openai.api_key = os.getenv("Azure_OpenAI")          # Your Azure OpenAI Key
# openai.api_version = ""
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("Azure_OpenAI"),
    azure_endpoint=os.getenv("Azure_link"),
    api_version="2023-05-15"  # or the version you have access to
)

def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model="embedding-model-name",  # e.g., "text-embedding-ada-002"
        deployment_id="your-deployment-id"  # Azure deployment name
    )
    return response.data[0].embedding

EMBEDDING_MODEL = "embed model name"  # Azure OpenAI embedding deployment
# COMPLETION_MODEL = "ychat completion model name (response model)"       # Azure OpenAI completion deployment

QDRANT_HOST = os.getenv("QDRANT-URL")  # e.g., "https://YOUR-QDRANT-URL
QDRANT_API_KEY = os.getenv("QDRANT_API")
COLLECTION = "rag_bot"

client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY
)

# def get_embedding(text):
#     """Generate an embedding using Azure OpenAI."""
#     response = openai.Embedding.create(
#         input=[text],
#         engine=EMBEDDING_MODEL
#     )
#     return response["data"][0]["embedding"]

def create_collection():
    """Create or recreate the Qdrant collection."""
    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)#COSINE is  a method of similarity search select size accroding to dim of embed model
# cool  what is size
    )
    
    def upload_vectors(index_data):
        """Upload data to Qdrant."""
    points = []
    for item in index_data:
        vector = get_embedding(item["chunk"])
        points.append(PointStruct(id=item["id"], vector=vector, payload=item))
    client.upsert(collection_name=COLLECTION, points=points)

def get_top_chunks(query, k=5):
    """Retrieve the most relevant chunks from Qdrant."""
    query_vector = get_embedding(query)
    results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector,
        limit=k
    )
    return [hit.payload["chunk"] for hit in results]

recipient_context = {}

# Stack to track question and answer history for backtracking
question_stack = []

def ask_and_respond(question, prev_q=None, prev_a=None):
    # Build a one-paragraph natural question based on recipient context
    context_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in recipient_context.items()])
     
    custom_prompt = (
        "You are a warm and creative assistant helping someone choose a thoughtful experience gift. "
        "You will rewrite the given question as a natural ,engaging prompt for the user and also respond warmly with 1 short sentence that shows understanding . "
        "IMPORTANT: Do NOT answer the question, do NOT add any explanations, introductions, or phrases like "
        "'Here's your rewritten prompt:' or 'That's a great question!'. "
        "Return ONLY the rewritten question prompt, with 40–60 words (2–3 sentences) in a single paragraph, based on the context below. "
        f"Original question: '{question}'\nContext:\n{context_summary}\n"
        "Make it concise, friendly, and conversational."
    )

    try:
        final_question = query_groq([{"role": "user", "content": (custom_prompt)}])
    except Exception as e:
        print("❌ AI Question Generation Error:", e)
        final_question = question  # fallback

    # Ask the generated paragraph-question
    answer = input(f"{final_question}\n> ")

    # Store context
    import re
    safe_q = re.sub(r'[^\w\s]', '', question).strip().lower()
    key = '_'.join(safe_q.split())[:40]
    recipient_context[key] = answer
    question_stack.append((key, question, answer))

    # Generate a follow-up conversational comment
    context_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in recipient_context.items()])
    # response_prompt = (
    #     f"You are helping someone choose a gift experience. Here's what you know so far:\n{context_summary}\n"
    #     f"Respond briefly and conversationally to their answer: '{answer}'"
    # )
    # messages = [{"role": "user", "content": response_prompt}]
    # try:
    #     ai_response = query_groq(messages)
    #     print(f"🤖 {ai_response}\n")
    # except Exception as e:
    #     print("❌ AI Error:", e)

    return question, answer
def go_back():
    """Go back to the previous question by removing the last entry from recipient_context and question_stack."""
    if not question_stack:
        return {"error": "No previous question to go back to."}
    key, question, answer = question_stack.pop()
    if key in recipient_context:
        del recipient_context[key]
    return {"question": question, "answer": answer}

import random

# Multiple variations for each question to add randomness and freshness
questions_alternatives = [
    [
        "Tell me a bit about your relationship with the person you're gifting—are they a close friend, partner, sibling, or someone else?",
        "How would you describe your connection with the person you’re planning to surprise?",
        "Who is the gift for, and what kind of bond do you share—friendship, family, love, or something else?",
        "What’s your relationship with this person—are they someone you see daily or reconnect with on special occasions?"
    ],
    [
        "What's the special occasion or reason behind this gift—birthday, anniversary, celebration, or just a surprise?",
        "What’s the occasion for this gift—something planned or a spontaneous surprise?",
        "Is this gift for a birthday, milestone, or just a ‘thinking of you’ kind of moment?",
        "Are you celebrating anything specific with this gift, or is it just to brighten their day?"
    ],
    [
        "If you had to describe their vibe or personality in a few words—like adventurous, calm, creative, or foodie—what would you say?",
        "What kind of energy or personality does the recipient bring—are they outgoing, introverted, artistic, or a thrill-seeker?",
        "How would you sum up their style or interests? Outdoorsy, luxury-loving, chill, high-energy?",
        "Give me a quick sense of their personality—what makes them light up?"
    ],
    [
        "What’s the general budget you’re planning to spend on this experience gift?",
        "Roughly how much would you like to spend on this experience?",
        "Do you have a price range in mind for this gift?",
        "Are you going for something small and sweet, or are you open to something more premium?"
    ],
    [
        "Is there a specific city or region you’d like the experience to take place in, or should it be something flexible or online?",
        "Where should this experience happen? In a specific city or should it be open to anywhere—or even virtual?",
        "Do you have a location in mind for the experience, or would you prefer something flexible or remote?",
        "Would you like the experience to be tied to a specific place, or is flexibility more important?"
    ]
]

def collect_gift_info():
    answers = []
    prev_q = prev_a = None
    for alternatives in questions_alternatives:
        q = random.choice(alternatives)
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

    # Example manual back call
    # print("⬅️ Going back:", go_back())

    follow_up_chat()
