
import json
from tqdm import tqdm
from Scraper import ScholarlyScraper, FirecrawlScraper, DBLPScraper, get_google_search_url, merge_publications_with_urls
from LLMInference import ResearchIdentifier, Topfields

def orchestrate(author_name,gsdata, limit=None):
    google_scraper = ScholarlyScraper(author_name)
    google_data = google_scraper.fetch_publications()
    dblp_scraper = DBLPScraper(author_name)
    dblp_data = dblp_scraper.fetch_publications()
    merged_publications = merge_publications_with_urls(google_data['publications'], dblp_data, author_name,gsdata, limit)
    research_identifier = ResearchIdentifier()
    for pub in merged_publications:
        summary = pub.get('summary', '')
        title = pub.get('title', '')
        if summary and title:
            subject_area_json = research_identifier.identify_research(title, summary)
            try:
                subject_area = json.loads(subject_area_json)
                pub['research_subject'] = subject_area.get('research_subject', 'N/A')
                pub['research_area'] = subject_area.get('research_area', 'N/A')
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for publication '{pub['title']}': {e}")
                pub['research_subject'] = 'N/A'
                pub['research_area'] = 'N/A'
    final_data_with_metadata = {
        'author': google_data['author'],
        'h_index': google_data['h_index'],
        'i10_index': google_data['i10_index'],
        'publications': merged_publications
    }
    
    with open(f"{author_name}_all.json", "w") as json_file:
        json.dump(final_data_with_metadata, json_file, indent=4)
    print(f"Corpus saved to {author_name}_all.json")
    return merged_publications,final_data_with_metadata


def pubsshort(author,merged_publications):
    final_data = {
        'author': author,
        'publication_mappings': [
            {
                'id': idx + 1,
                'title': pub['title'],
                'research_subject': pub.get('research_subject', 'N/A'),
                'research_area': pub.get('research_area', 'N/A')
            }
            for idx, pub in enumerate(merged_publications)
        ]
    }
    with open(f"{author}_publications.json", "w") as json_file:
        json.dump(final_data, json_file, indent=4)
    print(f"Data saved to {author}_publications.json")
    return final_data

def getinterests(author,gsdata,limit = None):
    # tops = Topfields()
    # result = tops.identify_research_fields(final_data["publication_mappings"], limit)
    result = {"interests":{}}
    result['interests'] = gsdata.get('interests')
    with open(f"{author}_interests.json", "w") as json_file:
        json.dump(result, json_file, indent=4)
    print(f"Interests saved to {author}_interests.json")
    return result

if __name__ == "__main__":
    orchestrate("Hari Mohan Pandey", limit=16)
