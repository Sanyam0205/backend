# README

## Overview

This script performs various tasks related to scraping research paper information from Google Scholar and DBLP. It fetches publication data, scrapes content summaries using Firecrawl, generates detailed summaries and author lists using OpenAI's models, and merges the data into a structured JSON format. Additionally, it supports saving the merged data to a file.

## Prerequisites

- Python 3.x
- Required libraries: `firecrawl`, `scholarly`, `googlesearch-python`, `tqdm`, `mistralai`, `requests`, `dotenv`
- OpenAI API Key stored in a `.env` file as `OPENAI_API_KEY`.
- Firecrawl API Key stored in a `.env` file as `FIRECRAWL_API_KEY`.

You can install the required libraries using:

```bash
pip install firecrawl scholarly googlesearch-python tqdm mistralai requests python-dotenv
```

---

## Class-wise Explanation

### 1. **`FirecrawlScraper` Class**

**Purpose**:
This class uses the Firecrawl API to scrape the summary of a provided URL.

**Functions**:
- `__init__(url: str)`: Initializes the class with the provided URL and sets up the Firecrawl API client.
- `scraper() -> str`: Fetches the summary from the Firecrawl API in markdown format. Returns `'N/A'` if there is an error.

**Inputs**:
- `url` (str): The URL of the research paper to be scraped.

**Outputs**:
- Returns the scraped summary in markdown format, or `'N/A'` if an error occurs.

---

### 2. **`ScholarlyScraper` Class**

**Purpose**:
Fetches publication data for a given faculty member from Google Scholar using the `scholarly` library.

**Functions**:
- `__init__(facultyname: str)`: Initializes the class with the faculty member's name.
- `fetch_publications() -> dict`: Fetches the publication data, including h-index and i10-index, for the faculty member.

**Inputs**:
- `facultyname` (str): The name of the faculty member whose publications are to be fetched.

**Outputs**:
- Returns a dictionary containing the author's name, h-index, i10-index, and a list of publications.

---

### 3. **`DBLPScraper` Class**

**Purpose**:
Fetches publication data for a given faculty member from DBLP.

**Functions**:
- `__init__(facultyname: str)`: Initializes the class with the faculty member's name.
- `fetch_publications() -> list`: Fetches the publication data for the faculty member from DBLP's API.

**Inputs**:
- `facultyname` (str): The name of the faculty member whose publications are to be fetched.

**Outputs**:
- Returns a list of publications from DBLP.

---

### 4. **`get_google_search_url(query: str) -> str` Function**

**Purpose**:
Fetches the URL of a publication using Google Search.

**Inputs**:
- `query` (str): The search query, typically the title of the publication along with the author's name.

**Outputs**:
- Returns the URL of the first search result or `None` if an error occurs.

---

### 5. **`get_summary_from_firecrawl(url: str, max_retries: int = 3) -> str` Function**

**Purpose**:
Fetches the summary of a publication from Firecrawl, with retry logic for reliability.

**Inputs**:
- `url` (str): The URL of the publication to be scraped.
- `max_retries` (int): The maximum number of retries if the Firecrawl API fails to return a valid summary.

**Outputs**:
- Returns the scraped summary or `'N/A'` if retries are exhausted.

---

### 6. **`merge_publications_with_urls(google_scholar_pubs: list, dblp_pubs: list, author: str, limit: int = None) -> list` Function**

**Purpose**:
Merges publications from Google Scholar and DBLP, fetches URLs and summaries for the first `limit` publications, and generates summaries and author lists using OpenAI models.

**Inputs**:
- `google_scholar_pubs` (list): List of publications from Google Scholar.
- `dblp_pubs` (list): List of publications from DBLP.
- `author` (str): Name of the faculty member.
- `limit` (int): The number of publications to process (optional).

**Outputs**:
- Returns a merged list of publications with URLs, summaries, and author lists.

---

### 7. **`format_json(author_name: str, h_index: str, i10_index: str, merged_pubs: list) -> dict` Function**

**Purpose**:
Formats the merged publication data into a structured JSON format.

**Inputs**:
- `author_name` (str): Name of the author.
- `h_index` (str): The h-index of the author.
- `i10_index` (str): The i10-index of the author.
- `merged_pubs` (list): List of merged publications.

**Outputs**:
- Returns a dictionary in JSON format with the structured data.

---

### 8. **`saver(filename: str, new_data: dict)` Function**

**Purpose**:
Saves the merged publication data to a JSON file.

**Inputs**:
- `filename` (str): The name of the file where the data will be saved.
- `new_data` (dict): The new data to be appended to the file.

**Outputs**:
- Saves the data to the specified file, creating the file if it doesn't exist.

---

## Error Handling

The script includes basic error handling mechanisms for common issues. Below is a table of potential errors, their causes, and possible solutions:

| Error                                      | Cause                                                              | Solution                                                                                             |
|--------------------------------------------|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `requests.exceptions.RequestException` in `FirecrawlScraper` | Issues with the Firecrawl API or network problems                   | Verify the Firecrawl API key and check for network connectivity.                                      |
| `JSONDecodeError` in `DBLPScraper`         | The response from DBLP is not valid JSON                           | Ensure the DBLP API is available and check the response format for any changes.                       |
| `KeyError` in `merge_publications_with_urls`| Missing keys in publication data from Google Scholar or DBLP        | Ensure that the publication data includes the required keys (`title`, `authors`, etc.).               |
| `FileNotFoundError` in `saver`             | The file to be written to does not exist                           | The function will create the file if it doesn't exist, so no additional handling is required.         |
| `requests.exceptions.RequestException` in `get_summary_from_firecrawl` | Issues with Firecrawl API or network problems                       | Retry the request or check for issues with the Firecrawl service.                                     |
| `Error during Google search`               | Google Search API returns no results or errors occur during the search | Check if the search query is correctly formatted and if Google Search is reachable.                   |

---

## Example Usage

### 1. Fetching Publications and Merging Data:
```python
google_scraper = ScholarlyScraper("Deepti Mehrotra")
google_data = google_scraper.fetch_publications()

dblp_scraper = DBLPScraper("Deepti Mehrotra")
dblp_pubs = dblp_scraper.fetch_publications()

merged_publications = merge_publications_with_urls(
    google_data['publications'], dblp_pubs, "Deepti Mehrotra", 5
)
```

### 2. Formatting Data into JSON:
```python
final_data = format_json(
    google_data['author'], 
    google_data['h_index'], 
    google_data['i10_index'], 
    merged_publications
)

saver("output.json", final_data)
print("Data saved to output.json")
```

