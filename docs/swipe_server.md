
# `swipe_server.py`

This file contains the FastAPI application for the swipe feature. It allows users to like, dislike, and skip experiences, and get recommendations based on their preferences.

## 1. Endpoints

### 1.1. `GET /start`

- **Description:** Gets initial experiences for the user.
- **Query Parameters:**
    - `user_id`: The user ID.
- **Response:**
    - `experiences`: A list of experiences.

### 1.2. `POST /recommendation`

- **Description:** Updates the swipes table and returns relevant recommendations.
- **Request Body:**
    - `user_id`: The user ID.
    - `likes`: A list of liked experience IDs.
    - `dislikes`: A list of disliked experience IDs.
    - `skips`: A list of skipped experience IDs.
- **Response:**
    - A list of recommended experiences.

## 2. Dependencies

- `fastapi`: For the web server.
- `uvicorn`: For running the FastAPI server.
- `pydantic`: For data validation.
- `supabase`: For database interactions.
- `swipe`: For the core logic of the swipe feature.
