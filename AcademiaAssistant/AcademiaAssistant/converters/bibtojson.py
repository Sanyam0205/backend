import subprocess
import json
import os
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
def convert_nested_json_string_to_json(json_string):
    try:
        json_object = json.loads(json_string)
        if "output" in json_object:
            json_object["output"] = json.loads(json_object["output"])
        return json_object
    except json.JSONDecodeError as e:
        print("Invalid JSON string:", e)
        return None

class LLMCleaner:
    """
    Class to clean the raw JSON string using OpenAI GPT and the beta chat completions parse endpoint.
    """
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key is missing.")
        self.client = OpenAI(api_key=openai_api_key)

    def cleanjson(self, json_string: str) -> dict:
        """
        Use OpenAI GPT to clean and structure the raw JSON string using the completions.parse endpoint.
        """
        prompt = f"Convert this string to structured JSON: {json_string}"

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an assistant that helps format and clean JSON."},
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

class BibtexToJsonConverter:
    """
    Class to handle conversion of BibTeX to JSON and cleaning using LLM.
    """
    def __init__(self, bibtex_file):
        self.bibtex_file = bibtex_file

    def convert_to_json(self):
        """
        Convert the BibTeX file to JSON format using the bib2x command-line tool.
        """
        if not self.bibtex_file or not os.path.exists(self.bibtex_file):
            raise FileNotFoundError(f"BibTeX file '{self.bibtex_file}' not found.")
        
        output_file = self.bibtex_file.replace('.bib', '.json')
        command = ['bib2x', '-i', self.bibtex_file, '-o', output_file, '-f', 'json']

        try:
            subprocess.run(command, check=True)
            print(f"Conversion successful. JSON saved to {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"Error running bib2x command: {e}")
            return None

    def clean_json_file(self, json_file):
        """
        Read the raw JSON from the file, pass it to the LLMCleaner, and return cleaned JSON.
        """
        with open(json_file, 'r', encoding='utf-8') as file:
            raw_json_string = file.read()

        cleaner = LLMCleaner()
        cleaned_json = cleaner.cleanjson(raw_json_string)
        return cleaned_json

    def save_json(self, cleaned_json, output_file):
        """
        Save the cleaned JSON to a file.
        """
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(cleaned_json, file, indent=4)
        print(f"Cleaned JSON data saved to {output_file}")

    def delete_json_file(self, json_file):
        """
        Delete the temporary JSON file created by bib2x after cleaning.
        """
        if os.path.exists(json_file):
            os.remove(json_file)
            print(f"Deleted the file: {json_file}")

if __name__ == "__main__":
    converter = BibtexToJsonConverter(bibtex_file=r"C:\Users\Shashwat.Sharma\Documents\Mokshayani\AcademiaAssistant\converters\test.bib")
    json_file = converter.convert_to_json()
    if json_file:
        cleaned_json = converter.clean_json_file(json_file)
        if cleaned_json:
            converter.save_json(cleaned_json, 'output_clean.json')
        converter.delete_json_file(json_file)
