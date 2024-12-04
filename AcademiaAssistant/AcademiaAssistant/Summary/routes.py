from fastapi import FastAPI, HTTPException, Query
from services import ProfileService, ResearchSummarizer
import os
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow frontend domain for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/profile/create")
def create_profile(author: str):
    """
    Create a profile for the given author and send data to MongoDB via Express.
    """
    profile = ProfileService()
    try:
        data = profile.create(author)
        return {"message": "Profile created successfully", "data": data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.get("/profile/publications")
def get_publications(author: str):
    """
    Get short publications for the given author.
    """
    profile = ProfileService()
    try:
        profile.create(author)  # Recreate the profile to ensure data is up to date
        return profile.pubsdatashort
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.get("/profile/interests")
def get_interests(author: str):
    """
    Get interests for the given author.
    """
    profile = ProfileService()
    try:
        profile.create(author)  # Recreate the profile to ensure data is up to date
        return profile.interests
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.post("/profile/search")
def search_profile(author: str, query: str):
    """
    Search for contexts related to the query for the given author.
    """
    profile = ProfileService()
    try:
        results = profile.searcher(author, query)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.get("/summary/generate")
def generate_summary():
    api_key = os.environ.get("OPENAI_API_KEY", "your_api_key_here")

    # Load the data files
    try:
        with open("Deepti Mehrotra_all.json") as data_file:
            full_data = json.load(data_file)
        with open("Deepti Mehrotra_interests.json") as interests_file:
            top_5_research_fields = json.load(interests_file)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Data file error: {e}")

    summarizer = ResearchSummarizer(api_key)
    try:
        summary_results = summarizer.process_data(full_data, top_5_research_fields)
        return summary_results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Define a Pydantic model to parse the JSON body
class QueryRequest(BaseModel):
    author: str
    query: str

@app.post("/profile/query")
def query_profile(query_request: QueryRequest):
    """
    Perform semantic search for a profile using author's name and a query.
    """
    profile_service = ProfileService(mongo_uri="mongodb://localhost:27017/", database="mydatabase")
    try:
        # Extract author and query from the JSON body
        results = profile_service.search_profile(query_request.author, query_request.query)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
