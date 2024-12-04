1# README

## Overview

This script orchestrates the process of scraping, merging, and enriching research publications from Google Scholar and DBLP using Firecrawl and OpenAI models. It fetches publication data for a given author, identifies research subjects and fields, and generates JSON files with the processed data. Additionally, it identifies the top research fields from the author's publications.

## Prerequisites

- Python 3.x
- Required libraries: `firecrawl`, `scholarly`, `googlesearch-python`, `tqdm`, `openai`, `requests`, `dotenv`
- OpenAI API Key stored in a `.env` file as `OPENAI_API_KEY`
- Firecrawl API Key stored in a `.env` file as `FIRECRAWL_API_KEY`

You can install the required libraries using:

```bash
pip install firecrawl scholarly googlesearch-python tqdm openai requests python-dotenv
```

Ensure the `.env` file is correctly configured with the necessary API keys:

```
OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

---

## Class-wise Explanation

### 1. **`ScholarlyScraper` Class**
- **Purpose**: Fetches publication data from Google Scholar for a given faculty member.
- **Inputs**: 
  - `facultyname` (str): Name of the faculty member.
- **Outputs**: 
  - A dictionary containing the author's name, h-index, i10-index, and a list of publications from Google Scholar.

### 2. **`DBLPScraper` Class**
- **Purpose**: Fetches publication data from DBLP for a given faculty member.
- **Inputs**:
  - `facultyname` (str): Name of the faculty member.
- **Outputs**: 
  - A list of publications from DBLP.

### 3. **`merge_publications_with_urls` Function**
- **Purpose**: Merges publication data from Google Scholar and DBLP, retrieves URLs via Google Search, and scrapes summaries using Firecrawl. It also uses OpenAI to identify authors and generate summaries.
- **Inputs**:
  - `google_scholar_pubs` (list): List of publications from Google Scholar.
  - `dblp_pubs` (list): List of publications from DBLP.
  - `author` (str): Name of the faculty member.
  - `limit` (int): The number of publications to process. If `None`, all publications are processed. 
    - **Explanation**: The `limit` parameter controls the number of publications processed by the script. For example, if `limit=16`, the first 16 publications will be processed (fetching URLs, scraping summaries, etc.). If `limit` is not provided, all publications will be processed.

- **Outputs**: 
  - A merged list of publications, including URLs, scraped summaries, research subjects, and research areas.

### 4. **`ResearchIdentifier` Class**
- **Purpose**: Uses OpenAI to identify the research subject and research area of a publication.
- **Functions**:
  - `identify_research(title: str, summary: str) -> dict`: Uses the publication title and summary to determine the research subject and area.
  
- **Inputs**:
  - `title` (str): The title of the publication.
  - `summary` (str): The summary of the publication.

- **Outputs**: 
  - A JSON object containing the research subject and research area.

### 5. **`Topfields` Class**
- **Purpose**: Uses OpenAI to identify the top research fields from the author's publications.
- **Functions**:
  - `identify_research_fields(publication_mappings: list, limit: int) -> dict`: Takes a list of publication mappings and returns the top 5 research fields.
  
- **Inputs**:
  - `publication_mappings` (list): A list of publications with their research subjects and areas.
  - `limit` (int): The number of publications to process. 

- **Outputs**: 
  - A JSON object containing the top 5 research fields.

---

## Functionality Explanation

### 1. **`orchestrate(author_name: str, limit: int = None)`**

This is the main function that orchestrates the entire process of scraping, merging, and enriching the research data.

#### Inputs:
- **`author_name`** (str): The name of the author for whom the data is to be scraped.
- **`limit`** (int, optional): The number of publications to process. If `None`, all publications will be processed. The `limit` parameter controls how many publications will have URLs and summaries fetched, and research areas identified. For example, `limit=16` means that only the first 16 publications will be processed.

#### Outputs:
- Generates and saves three JSON files:
  - **`{author_name}_all.json`**: A detailed JSON file containing all merged publication data, including URLs, summaries, research subjects, and research areas.
  - **`{author_name}_publications.json`**: A simplified JSON file containing the author's name, and each publication's title, research subject, and research area.
  - **`{author_name}_interests.json`**: A JSON file containing the top 5 research fields based on the publications.

---

## Orchestration Process

1. **Fetching Google Scholar Publications**:
   - The script uses `ScholarlyScraper` to fetch publication data for the given `author_name` from Google Scholar, including h-index and i10-index.

2. **Fetching DBLP Publications**:
   - The script uses `DBLPScraper` to fetch publication data for the same author from DBLP.

3. **Merging Publications**:
   - Publications from Google Scholar and DBLP are merged to form a unified dataset, avoiding duplicate entries.
   - For each publication, URLs are fetched using Google Search, and summaries are scraped using Firecrawl. Additionally, summaries and authors are generated using OpenAI models.

4. **Identifying Research Subjects and Areas**:
   - For each publication with a title and summary, the `ResearchIdentifier` class uses OpenAI to identify the research subject and research area. This information is appended to the publication data.

5. **Saving Detailed Data**:
   - The merged and enriched data is saved to `{author_name}_all.json`, which includes detailed information about each publication.

6. **Saving Simplified Data**:
   - A simplified version of the data, focusing on research subjects and areas, is saved to `{author_name}_publications.json`.

7. **Identifying Top Research Fields**:
   - Using the `Topfields` class, the top 5 research fields from the author's publications are identified and saved to `{author_name}_interests.json`.

---

## Example Usage

Here’s an example of how to run the orchestration for the author "Deepti Mehrotra" and limit the processing to the first 16 publications:

```python
if __name__ == "__main__":
    orchestrate("Deepti Mehrotra", limit=16)
```

This will:
1. Fetch and merge publications from Google Scholar and DBLP for "Deepti Mehrotra".
2. Process only the first 16 publications (fetch URLs, scrape summaries, identify research fields).
3. Save the detailed and simplified JSON files, along with the top 5 research fields.

---

## Error Handling

The script includes basic error handling mechanisms. Below is a table of potential errors, their causes, and solutions:

| Error                                      | Cause                                                             | Solution                                                                                            |
|--------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `requests.exceptions.RequestException`     | Issue with the Firecrawl API or network problems                   | Verify the Firecrawl API key and ensure that there is no network issue.                              |
| `KeyError` in `merge_publications_with_urls` | Missing keys in publication data from Google Scholar or DBLP        | Ensure that the publication data has the correct keys (`title`, `authors`, etc.).                    |
| `json.JSONDecodeError` in `orchestrate`    | Error parsing JSON from OpenAI's response                          | Ensure the response from OpenAI is valid JSON and add fallback for cases when the API call fails.     |
| `FileNotFoundError` in file writing        | The file to be written to does not exist                           | The function will create the file if it doesn't exist, so no additional handling is required.         |

---

## Conclusion

This orchestration script automates the process of gathering, enriching, and analyzing research publications for a given author. By using OpenAI models and scraping tools like Firecrawl, the script can generate useful insights and structured data for research purposes.
