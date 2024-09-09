import requests
from bs4 import BeautifulSoup
import time

headers = {
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Function to scrape details from IEEE
def scrape_ieee(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    og_description_meta = soup.find('meta', property='og:description')
    if og_description_meta:
        return og_description_meta['content'].strip()
    return None

# Function to scrape details from Springer
def scrape_springer(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    abstract_section = soup.find(class_='c-article-section__content')
    if abstract_section:
        return abstract_section.text.strip()
    return None

# Function to scrape details from ACM DL
def scrape_acm_dl(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    abstract_section = soup.find('section', id='abstract')
    if abstract_section:
        abstract_content_elem = abstract_section.find('div', role='paragraph')
        if abstract_content_elem:
            return abstract_content_elem.text.strip()
    return None

# Google Scholar URL for a specific profile
url = 'https://scholar.google.com/citations?user=SENrqMcAAAAJ&hl=en'
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Iterate through each publication item on the profile page
for item in soup.select('.gsc_a_tr'):
    print(item.select('.gsc_a_at')[0].text.strip())
    gs_pub_link = 'https://scholar.google.com' + item.select('a')[0]['href']
    print(gs_pub_link)
    print('======')

    stage2_response = requests.get(gs_pub_link, headers=headers)
    stage2_soup = BeautifulSoup(stage2_response.content, 'html.parser')
    journal_link = stage2_soup.find('a', class_='gsc_oci_title_link').get('href')
    # Extracting additional details from the publication page
    authors = stage2_soup.find(class_='gsc_oci_value').text.strip()
    publication_date = stage2_soup.find_all(class_='gsc_oci_value')[1].text.strip()
    book = stage2_soup.find_all(class_='gsc_oci_value')[2].text.strip()
    
    print("Journal Link", journal_link)
    print("Authors:", authors)
    print("Publication Date:", publication_date)
    print("Book:", book)

    # Determine domain and fetch abstract if applicable
    domain = None
    if 'ieee.org' in journal_link:
        domain = 'ieee'
    elif 'springer.com' in journal_link:
        domain = 'springer'
    elif 'dl.acm.org' in journal_link:
        domain = 'acm_dl'

    if domain:
        if domain == 'ieee':
            abstract = scrape_ieee(journal_link)
        elif domain == 'springer':
            abstract = scrape_springer(journal_link)
        elif domain == 'acm_dl':
            abstract = scrape_acm_dl(journal_link)

        if abstract:
            print("Abstract:", abstract)
        else:
            print("No abstract found for this domain.")
    else:
        print("Publication from a different domain.")

    print("--------")

    # Add a delay before making the next request
    time.sleep(5)
