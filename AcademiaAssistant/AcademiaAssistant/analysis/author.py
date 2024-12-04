import pymongo
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style
sns.set(style="whitegrid")

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # Replace with your database name
collection = db["profiles"]  # Replace with your collection name

# Fetch author data
author_name = "Deepti Mehrotra"
author_doc = collection.find_one({"master_all_data.name": author_name})

if not author_doc:
    print(f"Author '{author_name}' not found in the database.")
    exit()

# Extract data from master_all_data
master_all_data = author_doc.get("master_all_data", {})
masterdata = author_doc.get("masterdata", {})
publications = master_all_data.get("publications", [])
interests = master_all_data.get("interests", [])
cites_per_year = master_all_data.get("cites_per_year", {})
coauthors_data = masterdata.get("publications", [])

# General information
author_info = {
    "Name": master_all_data.get("name"),
    "Affiliation": master_all_data.get("affiliation"),
    "Email Domain": master_all_data.get("email_domain"),
    "H-Index": master_all_data.get("hindex"),
    "I10-Index": master_all_data.get("i10index"),
    "Total Citations": master_all_data.get("citedby"),
    "Research Interests": interests,
}

print("\nGeneral Information:")
for key, value in author_info.items():
    print(f"{key}: {value}")

# Authorship analysis
roles = defaultdict(int)
multi_authorship = defaultdict(int)
field_contributions = defaultdict(int)
coauthor_collaborations = defaultdict(int)

# Analyze publications
for i, pub in enumerate(publications):
    bib = pub.get("bib", {})
    title = bib.get("title", "Untitled").lower()
    pub_year = bib.get("pub_year", "Unknown")
    num_citations = pub.get("num_citations", 0)

    authors = coauthors_data[i].get("authors", [])
    if authors:
        if authors[0] == author_name:
            roles["First Author"] += 1
        elif authors[-1] == author_name:
            roles["Last Author"] += 1
        else:
            roles["Collaborative Author"] += 1
    else:
        roles["Single Author"] += 1

    if len(authors) == 1:
        multi_authorship["Single Author"] += 1
    else:
        multi_authorship["Multi Author"] += 1

    # Research area contributions
    for interest in interests:
        if interest.lower() in title:
            field_contributions[interest] += 1
            break
    else:
        field_contributions["General"] += 1

    # Coauthor collaborations
    for coauthor in authors:
        if coauthor != author_name:
            coauthor_collaborations[coauthor] += 1

# Print analysis
print("\nAuthorship Roles Distribution:")
for role, count in roles.items():
    print(f"{role}: {count}")

print("\nSingle vs Multi-Author Papers:")
for auth_type, count in multi_authorship.items():
    print(f"{auth_type}: {count}")

print("\nResearch Area Contributions:")
for field, count in field_contributions.items():
    print(f"{field}: {count}")

print("\nTop Coauthor Collaborations:")
top_coauthors = sorted(coauthor_collaborations.items(), key=lambda x: x[1], reverse=True)[:10]
for coauthor, count in top_coauthors:
    print(f"{coauthor}: {count} collaborations")

# Research output over time
years = sorted(cites_per_year.keys())
citations_over_time = [cites_per_year[year] for year in years]

print("\nCitations Over Time:")
for year, citations in zip(years, citations_over_time):
    print(f"{year}: {citations} citations")

# Visualization
fig, axes = plt.subplots(3, 2, figsize=(16, 20))
plt.subplots_adjust(top=0.95, hspace=0.5, wspace=0.4)

# Plot 1: Authorship roles (Pie Chart)
axes[0, 0].pie(roles.values(), labels=roles.keys(), autopct='%1.1f%%', colors=sns.color_palette("pastel"))
axes[0, 0].set_title("Authorship Roles Distribution", fontsize=14)

# Plot 2: Multi-authorship trends (Pie Chart)
axes[0, 1].pie(multi_authorship.values(), labels=multi_authorship.keys(), autopct='%1.1f%%', colors=sns.color_palette("muted"))
axes[0, 1].set_title("Single vs Multi-Author Papers", fontsize=14)

# Plot 3: Contributions by research area (Horizontal Bar Chart)
fields = list(field_contributions.keys())
field_counts = list(field_contributions.values())
axes[1, 0].barh(fields, field_counts, color=sns.color_palette("coolwarm", len(fields)))
axes[1, 0].set_title("Research Area Contributions", fontsize=14)
axes[1, 0].set_xlabel("Number of Contributions", fontsize=12)
axes[1, 0].set_ylabel("Research Areas", fontsize=12)

# Plot 4: Top coauthor collaborations (Bar Chart)
top_coauthor_names = [co[0] for co in top_coauthors]
top_coauthor_counts = [co[1] for co in top_coauthors]
axes[1, 1].bar(top_coauthor_names, top_coauthor_counts, color=sns.color_palette("pastel", len(top_coauthor_names)))
axes[1, 1].set_title("Top Coauthor Collaborations", fontsize=14)
axes[1, 1].set_xlabel("Coauthors", fontsize=12)
axes[1, 1].set_ylabel("Number of Collaborations", fontsize=12)
axes[1, 1].tick_params(axis='x', rotation=45)

# Plot 5: Citations over time (Line Plot)
axes[2, 0].plot(years, citations_over_time, marker="o", color="blue", linestyle="-")
axes[2, 0].set_title("Citations Over Time", fontsize=14)
axes[2, 0].set_xlabel("Year", fontsize=12)
axes[2, 0].set_ylabel("Citations", fontsize=12)

# Remove the empty subplot
fig.delaxes(axes[2, 1])

plt.show()
