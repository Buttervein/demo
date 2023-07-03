import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

now = datetime.now()
time = now.strftime("%Y%m%d_%H%M")

def scrapeAuthorAffiliations(pmid, title, date, journal):
    paper_url = "https://pubmed.ncbi.nlm.nih.gov" + pmid
    response = requests.get(paper_url)

    paper_soup = BeautifulSoup(response.content, "html.parser")
    authors = paper_soup.find("div", class_="authors-list")

    table = []

    for author in authors.find_all("span", class_ = "authors-list-item"):
        try:
            author_name = author.find("a", class_ = "full-name").text.strip()
        except:
            author_name = author.find("span", class_ = "full-name").text.strip()
        for affiliation in author.find_all("a", class_ = "affiliation-link"):
            if "Heidelberg" in affiliation['title']:
                table.append([author_name, affiliation['title'], paper_url, title, date, journal])

    return table

# for reference. original query: "Heidelberg"[Affiliation] AND "2022/06/20 00:00":"3000/01/01 05:00"[Date - Publication] AND ("computability"[All Fields] OR "computable"[All Fields] OR "computating"[All Fields] OR "computation"[All Fields] OR "computational"[All Fields] OR "computations"[All Fields] OR "compute"[All Fields] OR "computed"[All Fields] OR "computer s"[All Fields] OR "computers"[MeSH Terms] OR "computers"[All Fields] OR "computer"[All Fields] OR "computes"[All Fields] OR "computing"[All Fields] OR "computional"[All Fields] OR ("computability"[All Fields] OR "computable"[All Fields] OR "computating"[All Fields] OR "computation"[All Fields] OR "computational"[All Fields] OR "computations"[All Fields] OR "compute"[All Fields] OR "computed"[All Fields] OR "computer s"[All Fields] OR "computers"[MeSH Terms] OR "computers"[All Fields] OR "computer"[All Fields] OR "computes"[All Fields] OR "computing"[All Fields] OR "computional"[All Fields]) OR ("informatics"[MeSH Terms] OR "informatics"[All Fields] OR "informatic"[All Fields] OR "informatization"[All Fields]) OR ("bioinformatical"[All Fields] OR "bioinformatically"[All Fields] OR "computational biology"[MeSH Terms] OR ("computational"[All Fields] AND "biology"[All Fields]) OR "computational biology"[All Fields] OR "bioinformatic"[All Fields] OR "bioinformatics"[All Fields] OR "medical informatics"[All Fields))) AND (y_1[Filter]
base_url = "https://pubmed.ncbi.nlm.nih.gov/?term=Heidelberg%5BAffiliation%5D+AND+%28y_1%5BFilter%5D%29+AND+%28computational%5BAll+Fields%5D+OR+computer%5BAll+Fields%5D+OR+informatics%5BAll+Fields%5D+OR+bioinformatics%5BAll+Fields%5D%29&filter=datesearch.y_1&size=200&sort=relevance"
response = requests.get(base_url)
soup = BeautifulSoup(response.content, "html.parser")

max_pages = int(soup.find("label", class_ = "of-total-pages").text.split()[-1])

table_paper = []
table_authors = []

for page_no in range(max_pages):
    page = "&page=" + str(page_no + 1)

    # for reference. original query: "Heidelberg"[Affiliation] AND "2022/06/20 00:00":"3000/01/01 05:00"[Date - Publication] AND ("computability"[All Fields] OR "computable"[All Fields] OR "computating"[All Fields] OR "computation"[All Fields] OR "computational"[All Fields] OR "computations"[All Fields] OR "compute"[All Fields] OR "computed"[All Fields] OR "computer s"[All Fields] OR "computers"[MeSH Terms] OR "computers"[All Fields] OR "computer"[All Fields] OR "computes"[All Fields] OR "computing"[All Fields] OR "computional"[All Fields] OR ("computability"[All Fields] OR "computable"[All Fields] OR "computating"[All Fields] OR "computation"[All Fields] OR "computational"[All Fields] OR "computations"[All Fields] OR "compute"[All Fields] OR "computed"[All Fields] OR "computer s"[All Fields] OR "computers"[MeSH Terms] OR "computers"[All Fields] OR "computer"[All Fields] OR "computes"[All Fields] OR "computing"[All Fields] OR "computional"[All Fields]) OR ("informatics"[MeSH Terms] OR "informatics"[All Fields] OR "informatic"[All Fields] OR "informatization"[All Fields]) OR ("bioinformatical"[All Fields] OR "bioinformatically"[All Fields] OR "computational biology"[MeSH Terms] OR ("computational"[All Fields] AND "biology"[All Fields]) OR "computational biology"[All Fields] OR "bioinformatic"[All Fields] OR "bioinformatics"[All Fields] OR "medical informatics"[All Fields))) AND (y_1[Filter]
    url = base_url + page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")



    papers = soup.find_all("article", class_ = "full-docsum")
    for paper in papers:

        paper_title = paper.find("a", class_ = "docsum-title").text.strip()

        date_published = ' '.join(paper.find("span", class_ = "docsum-journal-citation").text.strip().split(".")[-2].split()[-3:])

        journal_published = paper.find("span", class_ = "docsum-journal-citation").text.strip().split(".")[0].strip()

        pmid = paper.find("a", class_ = "docsum-title")['href']

        paper_url = "https://pubmed.ncbi.nlm.nih.gov" + pmid

        table_paper.append([paper_title, date_published, journal_published, paper_url])

        # will also retrieve authors' affiliations    
        authors_affiliations = scrapeAuthorAffiliations(pmid, paper_title, date_published, journal_published)

        table_authors.extend(authors_affiliations)
        
    print(f"processed page {page_no + 1} of {max_pages}")


with open(f'papers_{time}.tsv', 'w', newline='', encoding='utf-8') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    writer.writerow(["Paper Title", "Date", "Journal", "URL"])
    for row in table_paper:
        writer.writerow(row)
with open(f'authors_{time}.tsv', 'w', newline='', encoding='utf-8') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    writer.writerow(["Author", "Affiliations", "URL", "Paper Title", "Date", "Journal"])
    for row in table_authors:
        writer.writerow(row)
            