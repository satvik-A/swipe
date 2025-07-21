import sys
from venv import logger
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
# from main import get_question, get_ans, get_top_chunks, go_back, reset_session, sessions
# from main import clear_all_sessions, get_all_sessions,follow_up_chat
 
    
    
    
    
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from swipe import get_top_chunks
import uuid

print("DEBUG: Starting server initialization")
load_dotenv()
load_dotenv()
load_dotenv()
load_dotenv(override=True)
print("DEBUG: Environment variables loaded")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
print(f"DEBUG: Supabase URL: {SUPABASE_URL}")
print(f"DEBUG: Supabase key exists: {bool(SUPABASE_KEY)}")

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API")
print(f"DEBUG: Qdrant URL: {QDRANT_URL}")
print(f"DEBUG: Qdrant API key exists: {bool(QDRANT_API_KEY)}")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing Supabase credentials.")
    logger.error("Missing Supabase credentials.")
    sys.exit(1)

if not QDRANT_URL or not QDRANT_API_KEY:
    print("WARNING: Missing Qdrant credentials. Will use fallback logic.")
    logger.warning("Missing Qdrant credentials. Will use fallback logic.")
    
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
print("DEBUG: Creating Supabase client")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("DEBUG: Supabase client created successfully")

app = FastAPI()
print("DEBUG: FastAPI app initialized")

from fastapi.middleware.cors import CORSMiddleware

print("DEBUG: Adding CORS middleware")
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # Allow all origins by default
    # You can specify specific origins if needed
    allow_origins=[
        "http://localhost:8080",  # local development
        "https://slash-rag-agent.onrender.com",
        "https://slash-experiences.netlify.app",  # fixed: added missing comma
        "http://localhost:5173", 
        "https://slashexperiences.in",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("DEBUG: CORS middleware added with allowed origins")

class SwipeRequest(BaseModel):
    user_id: str
    likes: List[str]  # List of UUIDs
    dislikes: List[str]  # List of UUIDs
    skips: List[str]  # List of UUIDs

@app.get("/start")
def get_initial_experiences(user_id: str):
    print(f"DEBUG: /start endpoint called for user_id: {user_id}")
    # Check if user already has history
    print(f"DEBUG: Checking if user {user_id} has previous swipe history")
    user_history = supabase.table("swipes").select("*").eq("user_id", user_id).execute().data
    print(f"DEBUG: User history found: {bool(user_history)}")
    if user_history:
        print(f"DEBUG: Returning existing status for user {user_id}")
        # return {"status": "existing", "message": "User has previous data."}
    # Update existing record in Supabase immediately
        print(f"DEBUG: Updating existing record for user {user_id}")
       

        current_record_response = supabase.table("swipes").select("*").eq("user_id", user_id).execute()
        current_record = current_record_response.data[0]
        print(f"DEBUG: Current record: {current_record}")
        
        # Merge arrays ensuring no duplicates across categories
        final_likes = current_record.get("likes", []) or []
        final_dislikes = current_record.get("dislikes", []) or []
        final_skips = current_record.get("skips", []) or []
        all_swiped = []
        all_swiped.extend(final_likes)
        all_swiped.extend(final_dislikes)
        all_swiped.extend(final_skips)
        # Merge arrays ensuring no duplicates across categories
        
        # Update Supabase immediately
    
        # Get all already swiped IDs from Supabase

        
        # Generate recommendations using Qdrant if available
        if final_likes:
            print(f"DEBUG: User has {len(final_likes)} liked experiences, generating recommendations")
            # Fetch liked experiences from Supabase
            print(f"DEBUG: Fetching liked experiences from Supabase")
            liked_experiences_response = supabase.table("experiences").select("*").in_("id", final_likes).execute()
            print(f"DEBUG: Found {len(liked_experiences_response.data) if liked_experiences_response.data else 0} liked experiences")
            
            if liked_experiences_response.data:
                # Extract tags from liked experiences
                all_tags = []
                for exp in liked_experiences_response.data:
                    print(f"DEBUG: Processing experience {exp.get('id')} with tags: {exp.get('tags')}")
                    if exp.get("tags"):
                        if isinstance(exp["tags"], list):
                            all_tags.extend(exp["tags"])
                        elif isinstance(exp["tags"], str):
                            all_tags.extend([t.strip() for t in exp["tags"].split(';')]) # remember this change from split(',') to split(';')
                
                print(f"DEBUG: All tags extracted: {all_tags}")
                print("all tags are:   " + str(all_tags))
                
                if all_tags:
                    # Use Qdrant to find similar experiences
                    unique_tags = list(set(all_tags))  # Remove duplicates
                    print(f"DEBUG: Unique tags: {unique_tags}")
                    tag_query = " ".join(unique_tags) # remember this edit
                    print(f"DEBUG: Tag query for Qdrant: {tag_query}")
                    
                    # qdrant_results = search_engine.search_similar(
                    #     query=f"Tags: {tag_query}",
                    #     top_k=20,
                    #     use_structured_parsing=True
                    # )
                    
                    print(f"DEBUG: Calling get_top_chunks with query: {tag_query}")
                    qdrant_results = get_top_chunks(tag_query, 15)
                    print(f"DEBUG: Qdrant results count: {len(qdrant_results)}")
                    
                    # Get experience IDs from Qdrant results, excluding already swiped
                    recommended_ids = []
                    for result in qdrant_results:
                        exp_id = result.get("supabase_id")
                        print(f"DEBUG: Processing result with ID: {exp_id}")
                        if exp_id and exp_id not in all_swiped and len(recommended_ids) < 7:
                            recommended_ids.append(exp_id)
                        if len(recommended_ids) < 7:
                            all_exp = supabase.table("experiences").select("*").execute()
                            for exp in all_exp.data:
                                if exp["id"] not in recommended_ids and exp["id"] not in all_swiped:
                                    recommended_ids.append(exp["id"])
                                    if len(recommended_ids) >= 7:
                                        break
                    
                    print(f"DEBUG: Recommended IDs after filtering: {recommended_ids}")
                    
                    # Fetch full experience data from Supabase
                    if recommended_ids:
                        print(f"DEBUG: Fetching full experience data for recommended IDs")
                        recommendations_response = supabase.table("experiences").select("*").in_("id", recommended_ids).execute()
                        print(f"DEBUG: Found {len(recommendations_response.data) if recommendations_response.data else 0} recommendations")
                        if recommendations_response.data:
                            print(f"DEBUG: Returning {len(recommendations_response.data[:7])} recommendations")
                            return recommendations_response.data[:7]
        
        # Fallback: Get random experiences excluding already swiped
        print(f"DEBUG: Using fallback recommendation logic")
        if all_swiped:
            print(f"DEBUG: Getting all experiences and filtering out {len(all_swiped)} already swiped ones")
            # Get all experiences and filter out already swiped ones
            all_experiences_response = supabase.table("experiences").select("*").execute()
            print(f"DEBUG: Found {len(all_experiences_response.data) if all_experiences_response.data else 0} total experiences")
            if all_experiences_response.data:
                # Filter out already swiped experiences
                filtered_experiences = [exp for exp in all_experiences_response.data if exp["id"] not in all_swiped]
                print(f"DEBUG: After filtering, {len(filtered_experiences)} experiences remain")
                print(f"DEBUG: Returning {len(filtered_experiences[:7])} filtered recommendations")
                return filtered_experiences[:7]
        else:
            print(f"DEBUG: No swipes yet, getting random recommendations")
            random_response = supabase.table("experiences").select("*").limit(7).execute()
            print(f"DEBUG: Found {len(random_response.data) if random_response.data else 0} random experiences")
            return random_response.data if random_response.data else []
        
        # print(f"DEBUG: No recommendations found, returning empty list")
        # return []
    

    # Get 7 random experiences
    selected_ids = ["0e99f7c2-e443-4e7a-8fb9-da84c1c2ac5b", # treasure hunt
                    "26b2b99a-e234-4a5a-88db-fe640671e770", # tasting menu
                    "08a038e9-f72f-473c-ab17-257c577813dc", # poetry
                    "1f4bda9e-e1a6-4da3-89ee-ba0f49556604", # paintball
                    "37c2968a-14d6-4f1c-9fc7-5f9d4e4df9c9", # zero gravity
                    "420b1069-2198-4b91-963d-ffc49dacdfbb", # dance fitness workshop
                    "ca19d186-8bf5-4620-b6e0-2bea93bcb606"] # adventure parks

    # Fetch experiences with those IDs
    experiences = []
    for id in selected_ids:
        result = supabase.table("experiences").select("*").eq("id", id).limit(1).execute().data
        if result:
            experiences.append(result[0])

    return {"experiences": experiences}

@app.post("/recommendation")
async def get_recommendations(request: SwipeRequest):
    """
    Update swipes table and return 5 relevant recommendations.
    Stateless: All data is immediately persisted to Supabase and discarded after response.
    """
    print(f"DEBUG: /recommendation endpoint called")
    print(f"DEBUG: Request data - user_id: {request.user_id}, likes: {len(request.likes)}, dislikes: {len(request.dislikes)}, skips: {len(request.skips)}")
    
    try:
        user_id = request.user_id
        new_likes = request.likes
        new_dislikes = request.dislikes
        new_skips = request.skips
        
        print(f"DEBUG: Processing recommendation request for user {user_id}")
        print(f"DEBUG: New likes: {new_likes}")
        print(f"DEBUG: New dislikes: {new_dislikes}")
        print(f"DEBUG: New skips: {new_skips}")
        
        logger.info(f"Processing recommendation request for user {user_id}")
        
        # Fetch current swipes record from Supabase
        print(f"DEBUG: Fetching current swipes record for user {user_id}")
        current_record_response = supabase.table("swipes").select("*").eq("user_id", user_id).execute()
        print(f"DEBUG: Current record found: {bool(current_record_response.data)}")
        
        if not current_record_response.data:
            # Create new record in Supabase immediately
            print(f"DEBUG: User {user_id} does not exist before. Creating a new record in swipes table")
            print("this user does not exit befour.    " + user_id + "      :   creating a new table even though this is /recomentded")
            insert_response = supabase.table("swipes").insert({
                "user_id": user_id,
                "likes": list(set(new_likes)) if new_likes else [],
                "dislikes": list(set(new_dislikes)) if new_dislikes else [],
                "skips": list(set(new_skips)) if new_skips else []
            }).execute()
            print(f"DEBUG: Insert response: {insert_response}")
            
            final_likes = new_likes
            final_dislikes = new_dislikes
            final_skips = new_skips
        else:
            # Update existing record in Supabase immediately
            print(f"DEBUG: Updating existing record for user {user_id}")
            current_record = current_record_response.data[0]
            print(f"DEBUG: Current record: {current_record}")
            
            # Merge arrays ensuring no duplicates across categories
            current_likes = current_record.get("likes", []) or []
            current_dislikes = current_record.get("dislikes", []) or []
            current_skips = current_record.get("skips", []) or []
            
            print(f"DEBUG: Current likes: {current_likes}")
            print(f"DEBUG: Current dislikes: {current_dislikes}")
            print(f"DEBUG: Current skips: {current_skips}")
            
            # Process new likes
            final_likes = current_likes.copy()
            for like_id in new_likes:
                if like_id not in final_likes:
                    final_likes.append(like_id)
                    # Remove from other arrays
                    current_dislikes = [id for id in current_dislikes if id != like_id]
                    current_skips = [id for id in current_skips if id != like_id]
            
            # Process new dislikes
            final_dislikes = current_dislikes.copy()
            for dislike_id in new_dislikes:
                if dislike_id not in final_dislikes:
                    final_dislikes.append(dislike_id)
                    # Remove from other arrays
                    final_likes = [id for id in final_likes if id != dislike_id]
                    current_skips = [id for id in current_skips if id != dislike_id]
            
            # Process new skips
            final_skips = current_skips.copy()
            for skip_id in new_skips:
                if skip_id not in final_skips:
                    final_skips.append(skip_id)
                    # Remove from other arrays
                    final_likes = [id for id in final_likes if id != skip_id]
                    final_dislikes = [id for id in final_dislikes if id != skip_id]
            
            print(f"DEBUG: Final likes after processing: {final_likes}")
            print(f"DEBUG: Final dislikes after processing: {final_dislikes}")
            print(f"DEBUG: Final skips after processing: {final_skips}")
            
            # Update Supabase immediately
            print(f"DEBUG: Updating swipes table for user {user_id}")
            update_response = supabase.table("swipes").update({
                "likes": final_likes,
                "dislikes": final_dislikes,
                "skips": final_skips,
                "updated_at": "now()"
            }).eq("user_id", user_id).execute()
            print(f"DEBUG: Update response: {update_response}")
        
        # Get all already swiped IDs from Supabase
        all_swiped = []
        all_swiped.extend(final_likes)
        all_swiped.extend(final_dislikes)
        all_swiped.extend(final_skips)
        print(f"DEBUG: All swiped IDs count: {len(all_swiped)}")
        
        # Generate recommendations using Qdrant if available
        if final_likes:
            print(f"DEBUG: User has {len(final_likes)} liked experiences, generating recommendations")
            # Fetch liked experiences from Supabase
            print(f"DEBUG: Fetching liked experiences from Supabase")
            liked_experiences_response = supabase.table("experiences").select("*").in_("id", final_likes).execute()
            print(f"DEBUG: Found {len(liked_experiences_response.data) if liked_experiences_response.data else 0} liked experiences")
            
            if liked_experiences_response.data:
                # Extract tags from liked experiences
                all_tags = []
                for exp in liked_experiences_response.data:
                    print(f"DEBUG: Processing experience {exp.get('id')} with tags: {exp.get('tags')}")
                    if exp.get("tags"):
                        if isinstance(exp["tags"], list):
                            all_tags.extend(exp["tags"])
                        elif isinstance(exp["tags"], str):
                            all_tags.extend([t.strip() for t in exp["tags"].split(';')]) # remember this change from split(',') to split(';')
                
                print(f"DEBUG: All tags extracted: {all_tags}")
                print("all tags are:   " + str(all_tags))
                
                if all_tags:
                    # Use Qdrant to find similar experiences
                    unique_tags = list(set(all_tags))  # Remove duplicates
                    print(f"DEBUG: Unique tags: {unique_tags}")
                    tag_query = " ".join(unique_tags) # remember this edit
                    print(f"DEBUG: Tag query for Qdrant: {tag_query}")
                    
                    # qdrant_results = search_engine.search_similar(
                    #     query=f"Tags: {tag_query}",
                    #     top_k=20,
                    #     use_structured_parsing=True
                    # )
                    
                    print(f"DEBUG: Calling get_top_chunks with query: {tag_query}")
                    qdrant_results = get_top_chunks(tag_query, 15)
                    print(f"DEBUG: Qdrant results count: {len(qdrant_results)}")
                    
                    # Get experience IDs from Qdrant results, excluding already swiped
                    recommended_ids = []
                    for result in qdrant_results:
                        exp_id = result.get("supabase_id")
                        print(f"DEBUG: Processing result with ID: {exp_id}")
                        if exp_id and exp_id not in all_swiped and len(recommended_ids) < 5:
                            recommended_ids.append(exp_id)
                        if len(recommended_ids) < 5:
                            all_exp = supabase.table("experiences").select("*").execute()
                            for exp in all_exp.data:
                                if exp["id"] not in recommended_ids and exp["id"] not in all_swiped:
                                    recommended_ids.append(exp["id"])
                                    if len(recommended_ids) >= 5:
                                        break
                    
                    print(f"DEBUG: Recommended IDs after filtering: {recommended_ids}")
                    
                    # Fetch full experience data from Supabase
                    if recommended_ids:
                        print(f"DEBUG: Fetching full experience data for recommended IDs")
                        recommendations_response = supabase.table("experiences").select("*").in_("id", recommended_ids).execute()
                        print(f"DEBUG: Found {len(recommendations_response.data) if recommendations_response.data else 0} recommendations")
                        if recommendations_response.data:
                            print(f"DEBUG: Returning {len(recommendations_response.data[:5])} recommendations")
                            return recommendations_response.data[:5]
        
        # Fallback: Get random experiences excluding already swiped
        print(f"DEBUG: Using fallback recommendation logic")
        if all_swiped:
            print(f"DEBUG: Getting all experiences and filtering out {len(all_swiped)} already swiped ones")
            # Get all experiences and filter out already swiped ones
            all_experiences_response = supabase.table("experiences").select("*").execute()
            print(f"DEBUG: Found {len(all_experiences_response.data) if all_experiences_response.data else 0} total experiences")
            if all_experiences_response.data:
                # Filter out already swiped experiences
                filtered_experiences = [exp for exp in all_experiences_response.data if exp["id"] not in all_swiped]
                print(f"DEBUG: After filtering, {len(filtered_experiences)} experiences remain")
                print(f"DEBUG: Returning {len(filtered_experiences[:5])} filtered recommendations")
                return filtered_experiences[:5]
        else:
            print(f"DEBUG: No swipes yet, getting random recommendations")
            random_response = supabase.table("experiences").select("*").limit(5).execute()
            print(f"DEBUG: Found {len(random_response.data) if random_response.data else 0} random experiences")
            return random_response.data if random_response.data else []
        
        print(f"DEBUG: No recommendations found, returning empty list")
        return []
    
    except Exception as e:
        print(f"ERROR: Exception in get_recommendations: {str(e)}")
        logger.error(f"Error in get_recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")
    
    finally:
        # Ensure search_engine is cleaned up (goes out of scope)
        search_engine = None




# Initialize Supabase client (only persistent connection)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_search_engine():
    """Create a fresh QdrantSearchEngine instance for each request."""
    try:
        if QDRANT_URL and QDRANT_API_KEY:
            # from qdrant_search import create_search_engine_with_session
            # return create_search_engine_with_session(
            #     url=QDRANT_URL,
            #     api_key=QDRANT_API_KEY
            # )
            if(1>0):
               help
        return None
    except Exception as e:
        logger.error(f"Error creating QdrantSearchEngine: {str(e)}")
        return None