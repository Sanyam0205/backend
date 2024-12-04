from pydantic import BaseModel, ValidationError
from openai import OpenAI
from dotenv import load_dotenv
import fitz  
import openai
from dotenv import load_dotenv
import os
load_dotenv()
import json
def convert_nested_json_string_to_json(json_string):
    try:
        json_object = json.loads(json_string)
        if "output" in json_object:
            json_object["output"] = json.loads(json_object["output"])
        return json_object
    except json.JSONDecodeError as e:
        print("Invalid JSON string:", e)
        return None
class Identifier(BaseModel):
    publication_name: str
    research_subject: str
    research_area: str

class ResearchIdentifier:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)

    def identify_research(self, title: str, summary: str) -> dict:
        prompt = f"From the given publication description, tell the research subject and research field. \
        For example, the paper 'Attention is All You Need' has 'Artificial Intelligence' as the subject \
        and 'Natural Language Generation' as the research field. Publication: {title}. Summary: {summary}"
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Classify the research subject and research area."},
                {"role": "user", "content": prompt},
            ],
            response_format=Identifier,
        )
        event = completion.choices[0].message.parsed
        return event.json()

class TopFieldsResponse(BaseModel):
    top_5_research_fields: str

class Topfields:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)

    def identify_research_fields(self, publication_mappings: list, limit: int) -> dict:
        """
        Sends the publication data to the LLM and retrieves the top 5 research fields.
        """
        limited_publications = publication_mappings[:limit]
        formatted_publications = "\n".join(
            [f"Title: {pub['title']}, Research Subject: {pub['research_subject']}, Research Area: {pub['research_area']}" 
             for pub in limited_publications]
        )
        prompt = f"OUTPUT IS A JSON with one key interests with list of interests as value. ONLY THIS KEY NO OTHER KEY. Given the following publications, identify the top 5 research fields. Group similar areas under broader categories when appropriate:\n{formatted_publications}. REMEMBER ONLY RETURN 5 INTEREST FIELDS"
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in classifying research fields."},
                {"role": "user", "content": prompt},
            ],
                response_format={ "type": "json_object" }
            )
            print(completion.choices[0].message.content)
            event = completion.choices[0].message.content
            print(event)
            return convert_nested_json_string_to_json(event)

        except (KeyError, ValidationError) as e:
            print(f"Error parsing LLM response: {e}")
            return {"error": "Failed to parse LLM response"}
class Authors(BaseModel):
    authors:list[str]

class GetAuthors:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)

    def findauthors(self, summary) -> list[str]:
        """
        Sends the publication data to the LLM and retrieves the authors list.
        """
        prompt = f"Given the scraped summary data of the research paper {summary}, give me a list of authors"
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are identifying authors from research paper scraped data"},
                {"role": "user", "content": prompt},
            ],
            response_format=Authors
        )
        try:
            event = completion.choices[0].message.parsed
            return event.dict()
        except (KeyError, ValidationError) as e:
            print(f"Error parsing LLM response: {e}")
            return {"error": "Failed to parse LLM response"}
class Summary(BaseModel):
    summary:str
class OpenAISummary:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)
    def generate_summary(self, scraper_summary: str) -> str:
        prompt = f"Given the following text, extract a detailed abstract that captures the main points: {scraper_summary}"
        for attempt in range(3):
            try:
                completion = self.client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert in summarization."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format=Summary
                )
                summary  = completion.choices[0].message.parsed
                return summary.dict()
            except (KeyError, IndexError) as e:
                print(f"Error processing OpenAI response (Attempt {attempt + 1}): {e}")
        return 'N/A'
    
openai.api_key = os.getenv("OPENAI_API_KEY")

class PostGeneration:
    def __init__(self,pdf_path):
        self.pdf = pdf_path
    def extract_pdf_sections(self):
        """Extracts the abstract, outcomes, conclusion, and future work from the research paper."""
        doc = fitz.open(self.pdf_path)
        abstract = ""
        outcomes = ""
        conclusion = ""
        future_work = ""
        for page in doc:
            text = page.get_text("text")
            content = text
            if "abstract" in text.lower():
                abstract = text.lower().split("abstract")[-1].split("\n")[0:5]  # Extract first few lines
            if "conclusion" in text.lower():
                conclusion = text.lower().split("conclusion")[-1].split("\n")[0:5]
            if "future work" in text.lower():
                future_work = text.lower().split("future work")[-1].split("\n")[0:5]
            if "outcomes" in text.lower():
                outcomes = text.lower().split("outcomes")[-1].split("\n")[0:5]

        return abstract, outcomes, conclusion, future_work,content

    def generate_social_media_post(self,abstract, outcomes, conclusion, future_work,content):
        """Generates a social media post based on extracted paper content."""
        prompt = f"""
        Write a mathematical research post for research community social media in a professional and engaging tone foocusing on research outcomes as if the author is summarizing their research for the public. Focus on the following:
        Be mathematical, technical, detail research oriented
        INCLUDE MATHEMATICAL EQUATIONS AND DETAILS WHEREVER REQUIRED
        PLEASE NOT DO NOT MISS TECHNICAL DETAILS, UNIQUENESS AND RESEARCH CRUX
        BE PROFESSIONAL
        Abstract: {abstract}
        Outcomes: {outcomes}
        Conclusion: {conclusion}
        Future Work: {future_work}
        Content = {content}
        The post should highlight the main findings, the impact of the research, and any future directions.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert research assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content

    def runner(self):
        abstract, outcomes, conclusion, future_work,content = self.extract_pdf_sections()
        post = self.generate_social_media_post(abstract, outcomes, conclusion, future_work,content)
        return post

    
class GetPubYear:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key is missing.")
        self.client = OpenAI(api_key=openai_api_key)

    def getyear(self, summary: str) -> dict:
        prompt = f"From the description return me the publication year{summary} in JSON format with a single key year. NO OTHER KEY"

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an assistant that finds publication year from data."},
                    {"role": "user", "content": prompt},
                ],
                response_format={ "type": "json_object" }
            )
            print(completion.choices[0].message.content)
            event = completion.choices[0].message.content
            print(event)
            return convert_nested_json_string_to_json(event)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {"error": "Failed to parse JSON output"}
        except Exception as e:
            print(f"Error cleaning JSON with OpenAI: {e}")
            return {"error": "Failed to clean JSON"}