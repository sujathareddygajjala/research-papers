import requests
import xml.etree.ElementTree as ET
import pandas as pd
from Bio import Entrez

# Set your email (required by PubMed API)
Entrez.email = "your_email@example.com"

def fetch_pubmed_papers(query, max_results=10):
    """Fetches research papers from PubMed based on a query."""
    search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    search_results = Entrez.read(search_handle)
    search_handle.close()

    pubmed_ids = search_results["IdList"]
    papers = []

    for pubmed_id in pubmed_ids:
        fetch_handle = Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml")
        fetch_results = fetch_handle.read()
        fetch_handle.close()

        root = ET.fromstring(fetch_results)

        # Extract relevant data
        article = root.find(".//PubmedArticle")
        if article is not None:
            title = article.findtext(".//ArticleTitle", default="N/A")
            pub_date = article.findtext(".//PubDate/Year", default="N/A")
            authors = [author.findtext("LastName", default="") + " " + author.findtext("ForeName", default="") 
                       for author in article.findall(".//Author") if author.find("LastName") is not None]

            affiliations = [affil.text for affil in article.findall(".//Affiliation") if affil.text]

            # Check for pharmaceutical/biotech affiliation
            if any("pharma" in aff.lower() or "biotech" in aff.lower() for aff in affiliations):
                papers.append({
                    "PubmedID": pubmed_id,
                    "Title": title,
                    "Publication Date": pub_date,
                    "Authors": ", ".join(authors),
                    "Affiliations": "; ".join(affiliations)
                })

    return papers

def save_to_csv(papers, filename="pubmed_results.csv"):
    """Saves fetched papers to a CSV file."""
    df = pd.DataFrame(papers)
    df.to_csv(filename, index=False)
    print(f"Saved {len(papers)} papers to {filename}")

if __name__ == "__main__":
    query = input("Enter search query: ")
    papers = fetch_pubmed_papers(query, max_results=20)
    if papers:
        save_to_csv(papers)
    else:
        print("No relevant papers found.")
