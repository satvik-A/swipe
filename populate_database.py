import csv
from openai import AzureOpenAI
from qdrant_client import QdrantClient, models
from supabase import create_client, Client
from credentials import (
    EMBEDDING_API_BASE, EMBEDDING_API_KEY, AZURE_OPENAI_API_VERSION, EMBEDDING_MODEL_NAME, 
    QDRANT_HOST, QDRANT_API_KEY, COLLECTION_NAME, VECTOR_SIZE, TEXT_COLUMN_NAME, CHUNK_SIZE, 
    CSV_FILE_PATH, SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE_NAME
)

# ---------------------------------------------------------------------
# Initialize Clients
# ---------------------------------------------------------------------
# Initialize AzureOpenAI client for embeddings
if not EMBEDDING_API_BASE or not EMBEDDING_API_KEY:
    print("Error: EMBEDDING_API_BASE and EMBEDDING_API_KEY environment variables must be set.")
    exit(1)

embedding_client = AzureOpenAI(
    api_key=EMBEDDING_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=EMBEDDING_API_BASE
)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY
)

# Initialize Supabase client
if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in credentials.py")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------
def fetch_data_from_supabase():
    """Fetch data from Supabase table and prepare it for Qdrant indexing."""
    print(f"Fetching data from Supabase table: {SUPABASE_TABLE_NAME}")
    
    try:
        # Fetch all data from Supabase table
        response = supabase.table(SUPABASE_TABLE_NAME).select("*").execute()
        
        if not response.data:
            print("No data found in Supabase table.")
            return []
        
        print(f"Found {len(response.data)} records in Supabase")
        
        index_data = []
        for i, row in enumerate(response.data):
            # Extract title from the title column
            title = row.get('title', '').strip() if row.get('title') else ''
            
            if not title:
                print(f"Warning: Row {i + 1} has no title content, skipping...")
                continue
            
            # Extract price
            price = 0.0
            if 'price' in row:
                try:
                    price = float(row['price']) if row['price'] is not None else 0.0
                except (ValueError, TypeError):
                    price = 0.0
            
            # Extract location
            location = row.get('location', '') or ''
            
            # Extract Supabase ID 
            supabase_id = row.get('id', '') or str(i)
            
            # Extract qdrant_id if it exists, otherwise use sequential number
            qdrant_id = row.get('qdrant_id', i)
            try:
                qdrant_id = int(qdrant_id)
            except (ValueError, TypeError):
                qdrant_id = i
            
            index_data.append({
                "csv_id": supabase_id,  # Original Supabase ID
                "qdrant_id": qdrant_id,  # Use qdrant_id from table or sequential number
                "original_row_num": i + 1,  # For traceability (1-indexed)
                "title": title,
                "price": price,
                "location": location
            })
        
        print(f"Successfully prepared {len(index_data)} records for embedding")
        return index_data
        
    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        return []

def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split large text into smaller chunks."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

def get_embedding(text_chunk):
    """Generate an embedding using Azure OpenAI."""
    try:
        response = embedding_client.embeddings.create(
            input=text_chunk,  # Changed from [text_chunk] to text_chunk
            model=EMBEDDING_MODEL_NAME
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding for chunk '{text_chunk[:30]}...': {e}")
        return None

def create_qdrant_collection_if_not_exists():
    """Create the Qdrant collection if it doesn't already exist."""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        if COLLECTION_NAME not in collection_names:
            print(f"Collection '{COLLECTION_NAME}' not found. Creating new collection.")
            qdrant_client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE)
            )
            print(f"Collection '{COLLECTION_NAME}' created successfully.")
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
    except Exception as e:
        print(f"Error checking or creating Qdrant collection: {e}")
        exit(1)

def upload_data_to_qdrant(index_data):
    """Upload data to Qdrant with title, price, and ID in payload."""
    points_to_upload = []
    print(f"Preparing {len(index_data)} items for Qdrant upload...")
    
    for i, item in enumerate(index_data):
        # Create embeddings from the title (not chunk)
        vector = get_embedding(item["title"])
        if vector:            # Create payload with all necessary data
            qdrant_payload = {
                "supabase_id": item["csv_id"],  # Original Supabase ID
                "title": item["title"],  # Full title
                "price": item["price"],  # Price from Supabase
                "location": item.get("location", ""),  # Optional location
                "original_row_num": item["original_row_num"]
            }
            points_to_upload.append(models.PointStruct(
                id=item["qdrant_id"],  # Use separate integer Qdrant ID
                vector=vector, 
                payload=qdrant_payload
            ))
        
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(index_data)} items for embedding...")

    if not points_to_upload:
        print("No valid points to upload after embedding. Exiting.")
        return

    print(f"Uploading {len(points_to_upload)} points to Qdrant collection '{COLLECTION_NAME}'...")
    try:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points_to_upload)
        print("Data has been embedded and uploaded to Qdrant successfully.")
        
        # Print statistics
        prices = [item["price"] for item in index_data]
        print(f"Uploaded {len(index_data)} experiences")
        print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"Average price: ${sum(prices) / len(prices):.2f}")
        
    except Exception as e:
        print(f"Error uploading data to Qdrant: {e}")

# ---------------------------------------------------------------------
# Main Script Logic
# ---------------------------------------------------------------------
def main_populate():
    """Main function to populate the Qdrant database from Supabase."""
    print("Starting database population process from Supabase...")

    # 1. Ensure Qdrant collection exists
    create_qdrant_collection_if_not_exists()

    # 2. Fetch and process data from Supabase
    index_data = fetch_data_from_supabase()
    if not index_data:
        print("No data found in Supabase. Exiting.")
        return

    # 3. Upload vectors to Qdrant
    upload_data_to_qdrant(index_data)

    print("Database population process finished.")

if __name__ == "__main__":
    main_populate()
