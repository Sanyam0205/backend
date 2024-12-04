from firecrawl.firecrawl import FirecrawlApp
from dotenv import load_dotenv
from scholarly import scholarly
from googlesearch import search
import os
import json
import requests
from tqdm import tqdm
import time
from mistralai import Mistral
from LLMInference import GetAuthors,OpenAISummary,GetPubYear
load_dotenv()

class FirecrawlScraper:
    def __init__(self, url):
        self.url = url
        self.app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    def scraper(self):
        """Fetches the summary of the URL using Firecrawl."""
        try:
            scrape_result = self.app.scrape_url(self.url)
            return scrape_result.get('markdown', '')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching summary from Firecrawl: {e}")
            return 'N/A'

# Google Scholar Scraper Class
class ScholarlyScraper:
    def __init__(self, facultyname):
        self.facultyname = facultyname

    def fetch_publications(self):
        """Fetches publication data from Google Scholar for a given faculty member."""
        search_query = scholarly.search_author(self.facultyname)
        author = scholarly.fill(next(search_query))
        publications = author.get('publications', [])
        
        publication_list = []
        for pub in publications:
            publication_list.append({
                'title': pub.get('bib', {}).get('title', 'N/A'),
                'publication year':{},
                'source': 'Google Scholar',
                'url': '',
                'authors':'',
                'summary': '',
                'scraper_summary':''
            })
        h_index = author.get('hindex', 'N/A')
        i10_index = author.get('i10index', 'N/A')
        
        return {
            'author': self.facultyname,
            'h_index': h_index,
            'i10_index': i10_index,
            'publications': publication_list
        }

# DBLP Scraper Class
class DBLPScraper:
    def __init__(self, facultyname):
        self.facultyname = facultyname

    def fetch_publications(self):
        """Fetches publication data from DBLP for a given faculty member."""
        url = f"https://dblp.org/search/publ/api?q={self.facultyname}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                hits = data.get('result', {}).get('hits', {}).get('hit', [])
                publication_list = []
                for hit in hits:
                    info = hit.get('info', {})
                    publication_list.append({
                        'title': info.get('title', 'N/A'),
                        'publication year':{},
                        'source': 'DBLP',
                        'authors':'',
                        'url': '',
                        'summary': '',
                        'scraper_summary':''
                    })
                return publication_list
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                return []
        else:
            print(f"Failed to fetch from DBLP with status code: {response.status_code}")
            return []

# Function to get the URL using Google Search
def get_google_search_url(query):
    """Uses googlesearch to fetch the URL of a publication."""
    try:
        result = search(query, num_results=1)
        for url in result:
            return url
    except Exception as e:
        print(f"Error during Google search: {e}")
    return None

# Function to get the summary using Firecrawl, with retries
def get_summary_from_firecrawl(url, max_retries=3):
    """Uses Firecrawl to get the summary of a publication, retries if 'N/A'."""
    for attempt in range(max_retries):
        summary = FirecrawlScraper(url).scraper()
        if summary != 'N/A':
            return summary
        print(f"Retry {attempt + 1} for URL: {url}")
        time.sleep(2)  # Optional delay between retries
    return 'N/A'

def get_citations(title, master_data):
    """
    This function takes a paper title and the path to the master JSON file,
    then returns the citation count corresponding to the paper title.
    """
    x = False
    for pub in master_data.get('publications', []):
        bib = pub.get('bib')
        master_title = bib.get('title')
        if master_title.lower() == title.lower():
            x = True
            return pub.get('num_citations', 0)
    if(x):
        print("Match found!!")
    return 0

def merge_publications_with_urls(google_scholar_pubs, dblp_pubs, author,gsdata, limit=None):
    all_publications = []
    titles_seen = set()
    
    # Remove duplicates between Google Scholar and DBLP
    for pub in google_scholar_pubs:
        if pub['title'] not in titles_seen:
            all_publications.append(pub)
            titles_seen.add(pub['title'])

    for pub in dblp_pubs:
        if pub['title'] not in titles_seen:
            all_publications.append(pub)
            titles_seen.add(pub['title'])

    if limit:
        for i, pub in enumerate(tqdm(all_publications[:limit], desc="Fetching URLs and summaries")):
            query = f"{pub['title']} {author}"
            url = get_google_search_url(query)
            pub['url'] = url or 'N/A'
            scraper_summary = get_summary_from_firecrawl(url) if url else 'N/A'
            run = OpenAISummary()
            result = run.generate_summary(scraper_summary)
            summary = result['summary']
            result = GetAuthors().findauthors(scraper_summary)
            authors =  result['authors']
            year = GetPubYear().getyear(scraper_summary)
            title = pub.get('title')
            if title:
                citation_count = get_citations(title, gsdata)
            else:
                citation_count = 0  
            pub['citations'] = citation_count
            pub['publication year'] = year
            pub['scraper_summary'] = scraper_summary  
            pub['summary'] = summary 
            pub['authors'] = authors
    else:
        for i, pub in enumerate(tqdm(all_publications, desc="Fetching URLs and summaries")):
            query = f"{pub['title']} {author}"
            url = get_google_search_url(query)
            pub['url'] = url or 'N/A'
            scraper_summary = get_summary_from_firecrawl(url) if url else 'N/A'
            run = OpenAISummary()
            result = run.generate_summary(scraper_summary)
            summary = result['summary']
            result = GetAuthors().findauthors(scraper_summary)
            authors =  result['authors']
            year = GetPubYear().getyear(scraper_summary)
            title = pub.get('title')
            if title:
                citation_count = get_citations(title, gsdata)
            else:
                citation_count = 0  
            pub['citations'] = citation_count
            pub['publication year'] = year
            pub['scraper_summary'] = scraper_summary  
            pub['summary'] = summary 
            pub['authors'] = authors
    return all_publications

def format_json(author_name, h_index, i10_index, merged_pubs):
    final_json = {
        'AUTHOR': author_name,
        'H INDEX': h_index,
        'I INDEX': i10_index,
        'PUBLICATIONS': [
            {
                'ID': idx + 1,
                'TITLE': pub['title'],
                'YEAR': pub['publication year'],
                'SOURCE': pub['source'],
                'AUTHORS': pub['authors'],
                'URL': pub['url'],
                'SCRAPER_SUMMARY': pub['scraper_summary'],
                'SUMMARY': pub['summary'] 
            }
            for idx, pub in enumerate(merged_pubs)
        ]
    }
    return final_json

def saver(filename, new_data):
    try:
        with open(filename, 'r+') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
            data.append(new_data)
            file.seek(0)
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        with open(filename, 'w') as file:
            json.dump([new_data], file, indent=4)

if __name__ == "__main__":
    google_scraper = ScholarlyScraper("Deepti Mehrotra")
    google_data = google_scraper.fetch_publications()

    dblp_scraper = DBLPScraper("Deepti Mehrotra")
    dblp_pubs = dblp_scraper.fetch_publications()
    merged_publications = merge_publications_with_urls(google_data['publications'], dblp_pubs, "Deepti Mehrotra", 5)

    final_data = format_json(
        google_data['author'], 
        google_data['h_index'], 
        google_data['i10_index'], 
        merged_publications
    )

    saver("output.json", final_data)
    print("Data appended to output.json")
