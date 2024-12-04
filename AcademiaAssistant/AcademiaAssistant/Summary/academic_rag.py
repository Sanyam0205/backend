import os
import json
from flask import Flask, jsonify
from typing import List, Dict
from openai import OpenAI
from flask_cors import CORS
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Check if CUDA is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class APIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = SentenceTransformer('all-MiniLM-L6-v2').to(device)

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
        highlighting key contributions, methodologies, and outcomes. Format the summary 
        with an introduction, main contributions, and conclusion.
        """
        user_prompt = f"""
        Summarize the research work of {author} in the areas of {', '.join(research_area)}. 
        Focus on their contributions to these fields, methodologies used, and significant outcomes. 
        Format the summary with an introduction, main contributions, and conclusion.
        """
        return self.api_client.generate_text(system_prompt, user_prompt)

    def generate_research_summary(self, author: str, research_area: str) -> str:
        system_prompt = f"""
        You are an academic assistant summarizing the research work of {author} in the field of {research_area}. 
        Provide a concise and accurate summary highlighting their key contributions, methodologies, and outcomes in this area.
        Format the summary with an introduction, main contributions, and conclusion.
        """
        user_prompt = f"""
        Summarize {author}'s research work in the field of {research_area}. Focus on their contributions, methodologies used, and significant outcomes in this area.
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

        if not isinstance(research_areas, list) or not research_areas:
            return {"error": "Research areas data is empty or not a list"}

        embeddings = self.api_client.get_embeddings(research_areas)
        documents = [
            {"embedding": emb, "research_area": area}
            for emb, area in zip(embeddings, research_areas)
        ]

        if not isinstance(top_5_research_fields, dict):
            return {"error": "Expected a dictionary for 'top_5_research_fields'"}

        interests = top_5_research_fields.get("interests", [])
        if not isinstance(interests, list):
            return {"error": "Expected 'interests' to be a list"}

        matched_areas = []
        for field in interests:
            query_embedding = self.api_client.get_embeddings([field])[0]
            similar_docs = self.similarity_searcher.find_similar(query_embedding, documents)
            matched_areas.extend([doc.get("research_area", "Unknown") for doc in similar_docs])

        matched_areas = list(set(matched_areas))[:5]

        author_name = data.get("author", "Unknown Author")
        general_summary = self.summary_generator.generate_general_summary(author_name, matched_areas)
        research_summaries = {}
        for research_area in matched_areas:
            research_summaries[research_area] = self.summary_generator.generate_research_summary(author_name, research_area)

        return {"general_summary": general_summary, "research_summaries": research_summaries}

@app.route('/generate-summary', methods=['GET'])
def generate_summary():
    api_key = os.environ.get("OPENAI_API_KEY", "your_api_key_here")

    with open("Deepti Mehrotra_all.json") as data_file:
        full_data = json.load(data_file)

    with open("Deepti Mehrotra_interests.json") as interests_file:
        top_5_research_fields = json.load(interests_file)

    data = full_data

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a dictionary for 'data'"}), 400

    summarizer = ResearchSummarizer(api_key)
    try:
        summary_results = summarizer.process_data(data, top_5_research_fields)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(summary_results)

if __name__ == "__main__":
    app.run(debug=True)