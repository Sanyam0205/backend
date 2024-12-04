import httpx  # To make HTTP requests
from gsmaster import Author
from orchestrator import orchestrate, pubsshort, getinterests
import os
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from openai import OpenAI
from pymongo import MongoClient
import json
# Check if CUDA is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class ProfileService:
    EXPRESS_SERVER_URL = "http://localhost:5000/api/profiles"  # Express server endpoint

    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/", database: str = "mydatabase"):
        self.gsdata = {}
        self.masterdata = {}
        self.pubsdata = []
        self.pubsdatashort = {}
        self.interests = {}
        self.summary_results = {}
        self.master_all_data = {} 
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.model = SentenceTransformer('all-MiniLM-L6-v2').to(device) # Store author_master_all data directly

    def create(self, author: str):
        try:
            author_instance = Author(author)
            self.gsdata = author_instance.getdata()
            self.master_all_data = self.gsdata  # Use the returned data directly
            print("\nGS data received and author_master_all data assigned\n")
        except Exception as e:
            print(f"Error getting GS data: {e}")
            raise ValueError(f"Failed to retrieve GS data: {e}")
        
        try:
            self.pubsdata, self.masterdata = orchestrate(author, self.gsdata, 1)
            print("\nPublication and Master data received\n")
        except Exception as e:
            print(f"Error getting Publication/Master data: {e}")
            raise ValueError(f"Failed to retrieve publication data: {e}")
        
        try:
            self.pubsdatashort = pubsshort(author, self.pubsdata)
            print("\nShort publication data received\n")
        except Exception as e:
            print(f"Error getting Short Publication data: {e}")
            raise ValueError(f"Failed to retrieve short publications: {e}")
        
        try:
            self.interests = getinterests(author, self.gsdata)
            print("\nInterests data received\n")
        except Exception as e:
            print(f"Error getting Interests: {e}")
            raise ValueError(f"Failed to retrieve interests: {e}")

        # Generate summary
        try:
            summarizer = ResearchSummarizer(api_key=os.environ.get("OPENAI_API_KEY", "your_api_key_here"))
            self.summary_results = summarizer.process_data({
                "author": author,
                "publications": self.pubsdata
            }, {"interests": self.interests})
            print("\nSummary generated\n")
            print("\n--- Generated Summary ---")
            print(f"General Summary: {self.summary_results['general_summary']}")
            for area, summary in self.summary_results['research_summaries'].items():
                print(f"\nResearch Area: {area}\nSummary: {summary}")
            print("\n--- End of Summary ---")
        except Exception as e:
            print(f"Error generating summary: {e}")
            raise ValueError(f"Failed to generate summary: {e}")
        
        # Prepare final data to send to Express
        final_data = {
            "author": author,
            "masterdata": self.masterdata,
            "short_publications": self.pubsdatashort,
            "interests": self.interests,
            "summary": self.summary_results,
            "master_all_data": self.master_all_data  # Include the data directly
        }

        # Send data to the Express server
        self._send_to_express(final_data)

        return final_data

    def _send_to_express(self, data):
        """
        Private method to send data to the Express server for MongoDB storage.
        """
        try:
            json_payload = json.dumps(data)
            payload_size = len(json_payload.encode('utf-8'))  # Get size in bytes
            print(f"Payload size: {payload_size / 1024:.2f} KB")  # Convert to KB for readability

            with httpx.Client() as client:
                response = client.post(self.EXPRESS_SERVER_URL, json=data)
                if response.status_code == 201:
                    print("Data successfully sent to MongoDB via Express server")
                else:
                    print(f"Failed to send data to MongoDB: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending data to Express server: {e}")

    def search_profile(self, author: str, query: str) -> List[Dict]:
        """
        Search for the author's profile in MongoDB, process the data, and perform semantic search.
        :param author: Author's name.
        :param query: Search query.
        :return: Top matching results.
        """
        # Fetch the author's data from the "profile" collection
        collection = self.db["profiles"]
        author_data = collection.find_one({"author": author})  # Query for the author document

        if not author_data:
            raise ValueError(f"Author '{author}' not found in the database.")

        # Access publications nested within masterdata
        masterdata = author_data.get("masterdata", {})
        publications = masterdata.get("publications", [])
        if not publications:
            raise ValueError(f"No publications found for author '{author}'.")

        # Prepare data for embedding
        texts = [
            f"{pub.get('title', '')} {pub.get('summary', '')}"
            for pub in publications
        ]
        if not texts:
            raise ValueError("No textual data available for embedding.")

        # Compute embeddings for the texts
        with torch.no_grad():
            doc_embeddings = self.model.encode(texts, convert_to_tensor=True)

        # Compute embedding for the query
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding.unsqueeze(0), doc_embeddings)[0]
        sorted_indices = similarities.argsort()[::-1]

        # Fetch top matching results
        top_results = [
            {
                "title": publications[i].get("title", ""),
                "summary": publications[i].get("summary", ""),
                "citations": publications[i].get("citations", 0),
                "research_area": publications[i].get("research_area", ""),
                "url": publications[i].get("url", ""),
                "similarity": float(similarities[i]),
            }
            for i in sorted_indices[:5]
        ]

        return top_results


class APIClient:

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = SentenceTransformer('all-MiniLM-L6-v2').to(device)  # Use the defined device

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        with torch.no_grad():
            embeddings = self.model.encode(texts, convert_to_tensor=True)
        return embeddings.cpu().numpy().tolist()

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content


class SummaryGenerator:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def generate_general_summary(self, author: str, research_area: List[str]) -> str:
        system_prompt = f"""
        You are an academic assistant summarizing research work in Computer Science, 
        focusing on {', '.join(research_area)}. Summarize the work concisely and accurately, 
        highlighting key contributions, methodologies, and outcomes.
        """
        user_prompt = f"""
        Summarize the research work of {author} in the areas of {', '.join(research_area)}. 
        Highlight contributions, methodologies, and outcomes concisely.
        """
        return self.api_client.generate_text(system_prompt, user_prompt)

    def generate_research_summary(self, author: str, research_area: str) -> str:
        system_prompt = f"""
        You are an academic assistant summarizing the research work of {author} in {research_area}. 
        Provide a concise and accurate summary highlighting key contributions, methodologies, and outcomes.
        """
        user_prompt = f"""
        Summarize {author}'s research work in {research_area}. Highlight contributions, methodologies, and outcomes.
        """
        return self.api_client.generate_text(system_prompt, user_prompt)


class SimilaritySearcher:
    @staticmethod
    def find_similar(query_embedding: List[float], documents: List[Dict]) -> List[Dict]:
        query_embedding = torch.tensor(query_embedding).to(device)
        doc_embeddings = torch.tensor([doc['embedding'] for doc in documents]).to(device)
        similarities = cosine_similarity(query_embedding.unsqueeze(0), doc_embeddings)[0]
        sorted_indices = similarities.argsort()[::-1]
        return [documents[i] for i in sorted_indices]


class ResearchSummarizer:
    def __init__(self, api_key: str):
        self.api_client = APIClient(api_key)
        self.summary_generator = SummaryGenerator(self.api_client)
        self.similarity_searcher = SimilaritySearcher()

    def process_data(self, data, top_5_research_fields: Dict):
        research_areas = [pub.get('research_area', '') for pub in data.get('publications', [])]

        embeddings = self.api_client.get_embeddings(research_areas)
        documents = [
            {"embedding": emb, "research_area": area}
            for emb, area in zip(embeddings, research_areas)
        ]

        interests = top_5_research_fields.get("interests", [])
        matched_areas = []
        for field in interests:
            query_embedding = self.api_client.get_embeddings([field])[0]
            similar_docs = self.similarity_searcher.find_similar(query_embedding, documents)
            matched_areas.extend([doc.get("research_area", "Unknown") for doc in similar_docs])

        matched_areas = list(set(matched_areas))[:5]

        author_name = data.get("author", "Unknown Author")
        general_summary = self.summary_generator.generate_general_summary(author_name, matched_areas)
        research_summaries = {
            research_area: self.summary_generator.generate_research_summary(author_name, research_area)
            for research_area in matched_areas
        }

        return {"general_summary": general_summary, "research_summaries": research_summaries}