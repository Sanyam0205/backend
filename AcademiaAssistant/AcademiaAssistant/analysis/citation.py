import pymongo
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style for aesthetic visuals
sns.set(style="whitegrid")

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # Replace with your database name
collection = db["profiles"]  # Replace with your collection name

# Fetch the author's document
author_name = "Deepti Mehrotra"
author_doc = collection.find_one({"master_all_data.name": author_name})

if not author_doc:
    print(f"Author '{author_name}' not found in the database.")
    exit()

# Extract relevant data from the document
author_data = author_doc.get("master_all_data", {})
publications = author_data.get("publications", [])
interests = author_data.get("interests", [])
h_index = author_data.get("hindex", "N/A")
i10_index = author_data.get("i10index", "N/A")
cites_per_year = author_data.get("cites_per_year", {})

# Sort and limit publications to top 50 (or 100) by citation count
top_publications = sorted(publications, key=lambda x: x.get("num_citations", 0), reverse=True)[:50]

# Trends Analysis: Citations per year for top papers and cumulative impact
citations_per_year = defaultdict(int, {int(year): cites for year, cites in cites_per_year.items()})
individual_paper_trends = defaultdict(lambda: defaultdict(int))

for pub in top_publications:
    pub_year = pub.get("bib", {}).get("pub_year")
    citations = pub.get("num_citations", 0)
    title = pub.get("bib", {}).get("title", "Untitled")
    if pub_year and citations:
        pub_year = int(pub_year)
        citations_per_year[pub_year] += citations
        individual_paper_trends[title][pub_year] = citations

# Calculate cumulative citations over the years
years = sorted(citations_per_year.keys())
cumulative_citations = []
total_citations = 0
for year in years:
    total_citations += citations_per_year[year]
    cumulative_citations.append(total_citations)

# Field Impact Analysis: Categorize papers by research area and provide citation counts
field_citations = defaultdict(int)
top_papers_by_topic = defaultdict(list)

for pub in top_publications:
    title = pub.get("bib", {}).get("title", "Untitled").lower()
    citations = pub.get("num_citations", 0)
    research_area_found = False

    # Identify primary research area based on interests
    for interest in interests:
        if interest.lower() in title:
            field_citations[interest] += citations
            top_papers_by_topic[interest].append((title, citations))
            research_area_found = True
            break

    if not research_area_found:
        field_citations["General"] += citations
        top_papers_by_topic["General"].append((title, citations))

# Sort top papers within each topic by citation count
for topic in top_papers_by_topic:
    top_papers_by_topic[topic] = sorted(top_papers_by_topic[topic], key=lambda x: x[1], reverse=True)

# Display Citation Analysis Results
print(f"Author: {author_name}")
print(f"H-Index: {h_index}")
print(f"I10-Index: {i10_index}")
print("\nCitations Per Year:")
for year, count in citations_per_year.items():
    print(f"  {year}: {count} citations")

print("\nCumulative Citations:")
for year, total in zip(years, cumulative_citations):
    print(f"  {year}: {total} cumulative citations")

print("\nField Impact Analysis:")
for field, count in field_citations.items():
    print(f"  {field}: {count} citations")
    print("  Top Papers:")
    for paper, citations in top_papers_by_topic[field][:3]:  # Display top 3 papers per topic
        print(f"    - {paper} ({citations} citations)")

print("\nResearch Interests:")
for interest in interests:
    print(f"  - {interest}")

# Visualization
plt.figure(figsize=(15, 10))

# Plot Citations per Year (Total and Cumulative)
plt.subplot(2, 2, 1)
plt.bar(years, [citations_per_year[year] for year in years], color='skyblue', label="Total Citations Per Year")
plt.plot(years, cumulative_citations, marker='o', color='orange', linestyle='--', linewidth=2, label="Cumulative Citations")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Citations", fontsize=12)
plt.title(f"Citation Trends for {author_name}", fontsize=14)
plt.legend()

# Plot Citations per Year for Top Individual Papers
plt.subplot(2, 2, 2)
for paper_title, yearly_data in list(individual_paper_trends.items())[:20]:  # Limit to top 10 papers
    paper_years = sorted(yearly_data.keys())
    paper_citations = [yearly_data[year] for year in paper_years]
    plt.plot(paper_years, paper_citations, marker='o', label=paper_title[:15] + '...')  # Truncate title for readability

plt.xlabel("Year", fontsize=12)
plt.ylabel("Citations", fontsize=12)
plt.title("Citation Trends for Top Individual Papers", fontsize=14)
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

# Plot Field Impact with `hue` to avoid future warning
plt.subplot(2, 2, 3)
fields = list(field_citations.keys())
citations = list(field_citations.values())
sns.barplot(x=citations, y=fields, hue=fields, dodge=False, palette="viridis")
plt.xlabel("Total Citations", fontsize=12)
plt.ylabel("Research Areas", fontsize=12)
plt.title("Field Impact by Research Area", fontsize=14)
plt.legend([], [], frameon=False)  # Remove redundant legend

# Plot Top Papers by Topic
plt.subplot(2, 2, 4)
for topic, papers in top_papers_by_topic.items():
    top_titles = [p[0][:15] + '...' for p in papers[:3]]  # Limit and truncate title for readability
    top_citations = [p[1] for p in papers[:3]]
    plt.barh(top_titles, top_citations, label=topic)

plt.xlabel("Citations", fontsize=12)
plt.ylabel("Top Papers", fontsize=12)
plt.title("Top Papers by Research Area", fontsize=14)
plt.legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Add space to prevent elements from cutting off
plt.show()
